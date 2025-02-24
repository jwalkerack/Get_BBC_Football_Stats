import json
import boto3
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_s3_client():
    return boto3.client("s3")

def save_match_data_to_s3(match_data, filename, bucket_name, foldername):
    s3 = get_s3_client()
    try:
        json_data = json.dumps(match_data, indent=2, ensure_ascii=False)
        s3.put_object(
            Bucket=bucket_name,
            Key=f"{foldername}/{filename}.json",
            Body=json_data.encode("utf-8"),
            ContentType="application/json"
        )
        logger.info(f"Match data uploaded to S3: {filename}.json")
        return True
    except ClientError as e:
        logger.error(f"AWS S3 Error: {e.response['Error']['Message']}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in save_match_data_to_s3: {e}")
        return False

def get_json_from_s3(bucket_name, file_key):
    s3 = get_s3_client()
    try:
        response = s3.get_object(Bucket=bucket_name, Key=file_key)
        return json.loads(response["Body"].read().decode("utf-8"))
    except ClientError as e:
        logger.error(f"S3 Error: {e.response['Error']['Message']}")
        return None
    except json.JSONDecodeError:
        logger.error("Error decoding JSON from S3")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in get_json_from_s3: {e}")
        return None

def update_json_in_s3(updated_dict, bucket_name, file_key):
    if not updated_dict:
        logger.error("Attempted to update S3 with empty JSON data.")
        return False

    s3 = get_s3_client()
    try:
        json_data = json.dumps(updated_dict, indent=2, ensure_ascii=False)
        s3.put_object(
            Bucket=bucket_name,
            Key=file_key,
            Body=json_data.encode("utf-8"),
            ContentType="application/json"
        )
        logger.info(f"JSON updated in S3: {bucket_name}/{file_key}")
        return True
    except ClientError as e:
        logger.error(f"AWS S3 Error: {e.response['Error']['Message']}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in update_json_in_s3: {e}")
        return False

