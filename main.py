import argparse
import base64
import json
import logging
import os
import subprocess
from datetime import datetime, timedelta, timezone

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from dotenv import load_dotenv

logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

if os.getenv("ENV") != "production":
    logger.info("ローカル環境の為.envをロードします")
    load_dotenv()
else:
    logger.info("本番環境の為、環境変数はBatch Job Definitionからロードします")

def get_secret(secret_name : str, region_name : str, aws_profile : str) -> str:

    secret_name = secret_name
    region_name = region_name

    session = boto3.session.Session(profile_name=aws_profile)
    client = session.client(service_name="secretsmanager", region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        # Decrypts secret using the associated KMS key.
        secret = get_secret_value_response["SecretString"]
        return secret
    except ClientError as e:
        logger.error(f"Failed to retrieve secret: {e}", exc_info=True)
        raise


def arg_parser() -> str:
    parser = argparse.ArgumentParser(
        description="--target-date にて指定日付のGA4 BigQueryデータをS3に転送します。日付がない場合は自動的に2日前のデータを取得します。"
    )
    parser.add_argument("--target-date", type=str, help="YYYY-MM-DD形式の日付を指定してください。")
    args = parser.parse_args()
    if args.target_date:
        target_date = convert_date_format(args.target_date)
        logger.info(f"指定された日付: {target_date}で実行します")
    else:
        target_date = (datetime.now(timezone.utc) + timedelta(hours=9) - timedelta(days=2)).strftime("%Y%m%d")
        logger.info(f"指定された日付がないため、2日前の日付: {target_date}で実行します")
    return target_date


def convert_date_format(date_str) -> str:
    try:
        # Parse the input date string as a datetime object
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        # Convert to YYYYMMDD format using strftime
        return date_obj.strftime("%Y%m%d")
    except ValueError:
        # Raise ValueError if the date string is not in the expected format
        raise ValueError("Invalid date format")


def run_bq_extract(converted_date: str, env : dict, secret_manager_json : dict) -> None:
    logger.info(f"GA4 BigQueryからGCSにデータをエクスポートします。")
    logger.info(f"テーブル : {secret_manager_json[env['AWS_SECRETS_MANAGER_BIGQUERY_DATASET_ID']].replace(':','.')}.events_{converted_date}")
    logger.info(f"エクスポート先 : gs://{secret_manager_json[env['AWS_SECRETS_MANAGER_GCS_EXPORT_URI']]}/event_date_part={converted_date}/export-*.parquet")
    query = (
        "bq extract "
        f"--location={env['GCS_REGION_NAME']} "
        "--destination_format=PARQUET "
        "--compression=SNAPPY "
        "--print_header=true "
        f"{secret_manager_json[env['AWS_SECRETS_MANAGER_BIGQUERY_DATASET_ID']]}.events_{converted_date} "
        f"gs://{secret_manager_json[env['AWS_SECRETS_MANAGER_GCS_EXPORT_URI']]}/event_date_part={converted_date}/export-*.parquet"
    )
    result = subprocess.run(["sh", "-c", query], capture_output=True, text=True, env=env)
    if result.returncode != 0:
        logger.error(f"Command failed with error: {result.stderr}")
        logger.error(f"Command output: {result.stdout}")
        raise RuntimeError(f"Command failed with error: {result.stderr}")
    else:
        logger.info(f"Command output: {result.stdout}")


def gcs_to_s3(env : dict, secret_manager_json : dict) -> None:
    logger.info(f"GCSからS3にデータを転送します。")
    logger.info(f"転送先 :s3://{secret_manager_json[env['AWS_SECRETS_MANAGER_S3_TRANSFER_URI']]} ")
    query = (
        "gcloud storage rsync "
        f"gs://{secret_manager_json[env['AWS_SECRETS_MANAGER_GCS_EXPORT_URI']]} "
        f"s3://{secret_manager_json[env['AWS_SECRETS_MANAGER_S3_TRANSFER_URI']]} "
        "--recursive"
    )

    result = subprocess.run(["sh", "-c", query], capture_output=True, text=True, env=env)

    if result.returncode != 0:
        logger.error(f"Command failed with error: {result.stderr}")
        logger.error(f"Command output: {result.stdout}")
        raise RuntimeError(f"Command failed with error: {result.stderr}")
    else:
        logger.info(f"Command output: {result.stdout}")


def gcloud_auth(env : dict) -> None:
    query = "gcloud auth activate-service-account --key-file=/tmp/credentials.json"
    result = subprocess.run(["sh", "-c", query], capture_output=True, text=True, env=env)
    if result.returncode != 0:
        logger.error(f"Command failed with error: {result.stderr}")
        logger.error(f"Command output: {result.stdout}")
        raise RuntimeError(f"Command failed with error: {result.stderr}")
    else:
        logger.info(f"Command output: {result.stdout}")

def gcloud_initialize(project_id : str) -> None:
    query = f"gcloud config set project {project_id}"
    result = subprocess.run(["sh", "-c", query], capture_output=True, text=True, env=env)
    if result.returncode != 0:
        logger.error(f"Command failed with error: {result.stderr}")
        logger.error(f"Command output: {result.stdout}")
        raise RuntimeError(f"Command failed with error: {result.stderr}")
    else:
        logger.info(f"Command output: {result.stdout}")

if __name__ == "__main__":
    try:
        target_date = arg_parser()
        env = os.environ.copy()
        env["GOOGLE_APPLICATION_CREDENTIALS"] = "/tmp/credentials.json"
        aws_profile = None if "AWS_BATCH_JOB_ID" in os.environ else env['AWS_PROFILE_NAME']

        if aws_profile is not None:
            env["AWS_PROFILE"] = aws_profile
        env["PATH"] = env["PATH"] + ":/google-cloud-sdk/bin"

        ga4_bigquery_to_s3_setting = json.loads(get_secret(
                secret_name=env['AWS_SECRETS_MANAGER_NAME'],
                region_name=env['AWS_REGION'],
                aws_profile=aws_profile
            ))
        base64_encoded_credentials = ga4_bigquery_to_s3_setting[env['AWS_SECRETS_MANAGER_BASE64_ENCODED_KEY_NAME']]
        json_str = base64.b64decode(base64_encoded_credentials).decode("utf-8")
        data = json.loads(json_str)

        with open("/tmp/credentials.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        gcloud_initialize(ga4_bigquery_to_s3_setting[env['AWS_SECRETS_MANAGER_BIGQUERY_DATASET_ID']].split(':')[0])
        gcloud_auth(env)
        run_bq_extract(target_date, env, ga4_bigquery_to_s3_setting)
        gcs_to_s3(env, ga4_bigquery_to_s3_setting)
        logger.info(f"Data successfully transferred for date: {target_date}")
    except (BotoCoreError, ClientError) as e:
        logger.error(f"S3 error: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"General error: {e}", exc_info=True)
        raise
