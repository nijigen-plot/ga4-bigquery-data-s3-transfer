# 内容

GA4 BigQuery ExportデータをAWS S3に転送しAthenaでクエリができるようにします

# GCP側手動対処

## サービスアカウントの秘密鍵

用いるサービスアカウントは以下コマンド実行したのち文字列をAWS Secret Managerへ登録
```
$ base64 service_account_secret_key.json | tr -d '\n'
```

# ローカル実行

## --build-argでGCP_PROJECT_ID=を指定

```
$ docker build -t ga4-bigquery-to-s3 . --build-arg GCP_PROJECT_ID=
$ docker run -v ~/.aws:/root/.aws -v $(pwd)/.env:/app/.env ga4-bigquery-to-s3:latest
```

## ECR 登録

AWS ECRに以下コマンドを使って事前にリポジトリを登録しておく
```
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
aws ecr create-repository --repository-name ga4-bigquery-to-s3 --region $AWS_REGION --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE
```
