import boto3
import os

CurrentAction = 'Production'

if CurrentAction == 'Testing':
    S3_BUCKET = os.getenv("S3_BUCKET", "datapulledraw")
    S3_FILE_KEY = os.getenv("S3_FILE_KEY", "DB_KEYS/match_id_dev.json")
    S3_FOLDER = os.getenv("S3_FOLDER", "DB_DATA_DEV")
elif CurrentAction == 'Production':
    S3_BUCKET = os.getenv("S3_BUCKET", "datapulledraw")
    S3_FILE_KEY = os.getenv("S3_FILE_KEY", "DB_KEYS/match_id.json")
    S3_FOLDER = os.getenv("S3_FOLDER", "DB_DATA")


def get_s3_client():
    return boto3.client("s3")
