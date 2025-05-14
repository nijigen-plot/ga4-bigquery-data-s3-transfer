# 内容

GA4 BigQuery ExportデータをAWS S3に転送しAthenaでクエリができるようにします

# GCP側手動対処

## サービスアカウントの秘密鍵

用いるサービスアカウントは以下コマンド実行したのち文字列をAWS Secret Managerへ登録
```
$ base64 voltaic-country-281210-1e6a73a14fc6.json | tr -d '\n'
```

# ローカル実行

--build-argでGCP_PROJECT_ID=を指定
```
$ docker build -t ga4-bigquery-to-s3 . --build-arg GCP_PROJECT_ID=
$ docker run -v ~/.aws:/root/.aws -v $(pwd)/.env:/app/.env ga4-bigquery-to-s3:latest
```
