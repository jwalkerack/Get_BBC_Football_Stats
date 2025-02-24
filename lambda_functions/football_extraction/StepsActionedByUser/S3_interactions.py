import json
import logging
#from lambda_function.football_extraction.config import get_s3_client ,S3_BUCKET,S3_FILE_KEY, S3_FOLDER

from lambda_functions.football_extraction.StepsActionedByUser.config_Dev import get_s3_client ,S3_BUCKET,S3_FILE_KEY, S3_FOLDER
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def delete_keys_master(keys_to_delete):
    """
    Takes a list of identifiers and deletes them from the JSON database in S3.
    """
    s3 = get_s3_client()
    try:
        # Step 1: Download JSON from S3
        response = s3.get_object(Bucket=S3_BUCKET, Key=S3_FILE_KEY)
        json_data = json.loads(response['Body'].read().decode('utf-8'))  # Load JSON
        deletions = []

        # Step 2: Delete specified keys
        if 'identifiers' in json_data:
            for key1 in keys_to_delete:
                if key1 in json_data['identifiers']:
                    json_data['identifiers'].pop(key1, None)  # Safe delete (avoids KeyError)
                    deletions.append(key1)

        # Step 3: Upload modified JSON back to S3
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=S3_FILE_KEY,
            Body=json.dumps(json_data, indent=4)  # Pretty format for readability
        )
        logger.info(f"deleted {deletions}")

        print(f"Successfully deleted {len(keys_to_delete)} keys from {S3_FILE_KEY}")
        return True

    except s3.exceptions.NoSuchKey:
        print(f"Error: {S3_FILE_KEY} not found in bucket {S3_BUCKET}")
        return False

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return False

def delete_all_json_files():
    """
    Deletes all JSON files stored in the 'DB_DATA/' directory in the S3 bucket.

    Returns:
        bool: True if deletion was successful, False otherwise.
    """
    s3 = get_s3_client()

    try:
        response = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=S3_FOLDER)

        if "Contents" in response:
            objects_to_delete = [{"Key": obj["Key"]} for obj in response["Contents"]]

            s3.delete_objects(Bucket=S3_BUCKET, Delete={"Objects": objects_to_delete})
            logger.info(f"Deleted {len(objects_to_delete)} JSON files from {S3_BUCKET}/{S3_FOLDER}")

        else:
            logger.info(f"No JSON files found in {S3_BUCKET}/{S3_FOLDER}")

        return True

    except Exception as e:
        logger.error(f"Error deleting JSON files: {e}")
        return False

def reset_match_id_json():
    """
    Resets the match_id.json file in S3 to contain an empty 'identifiers' dictionary.

    Returns:
        bool: True if reset is successful, False otherwise.
    """
    s3 = get_s3_client()

    try:
        empty_json = {"identifiers": {}}

        json_data = json.dumps(empty_json, indent=2, ensure_ascii=False)

        s3.put_object(
            Bucket=S3_BUCKET,
            Key=S3_FILE_KEY,
            Body=json_data.encode("utf-8"),
            ContentType="application/json"
        )

        logger.info(f"Successfully reset {S3_BUCKET}/{S3_FILE_KEY}")
        return True

    except Exception as e:
        logger.error(f"Error resetting match_id.json: {e}")
        return False

