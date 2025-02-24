from lambda_functions.football_extraction.StepsActionedByUser.S3_interactions import reset_match_id_json , delete_all_json_files
from lambda_functions.football_extraction.StepsActionedByUser.set_up_elements import get_flood_months
from lambda_functions.football_extraction.StepsActionedByUser.models import leagues
from lambda_functions.football_extraction.StepsActionedByUser.process_games_dp import process_games_for_months_TD
import json

monthsOfInterest = [
    "2024-08", "2024-09", "2024-10", "2024-11", "2024-12",
    "2025-01" , "2025-02", "2025-03", "2025-04"
]

monthsOfInterestToJan = [
    "2024-08", "2024-09", "2024-10", "2024-11", "2024-12",
    "2025-01"
]

monthsOfInterestToFeb= [
    "2024-08", "2024-09", "2024-10", "2024-11", "2024-12",
    "2025-01", "2025-02"
]

def lambda_handler_flood(event, context):
    """Flood AWS Lambda handler."""
    reset_match_id_json()
    delete_all_json_files()
    monthsToProcess = get_flood_months(monthsOfInterestToFeb)
    process_games_for_months_TD(monthsToProcess, leagues)
    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Flood completed!"})
    }


