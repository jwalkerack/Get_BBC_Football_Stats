from datetime import datetime, timedelta
import boto3
import json
import logging


logger = logging.getLogger()
logger.setLevel(logging.INFO)





def get_flood_months(gameYearMonths):
    """
    Filters and returns a list of YYYY-MM values up to yesterday's month.

    Args:
        gameYearMonths (list): A list of YYYY-MM formatted strings.

    Returns:
        list: Filtered list of months up to the latest available month.
    """
    try:
        if not gameYearMonths:
            logger.warning("No game year months provided, returning an empty list.")
            return []

        today = datetime.now()
        yesterday = today - timedelta(days=1)
        latest_month = yesterday.strftime("%Y-%m")

        flood_months = [month for month in gameYearMonths if month <= latest_month]

        if not flood_months:
            logger.warning("No manualActions months available before the latest month.")

        return flood_months

    except Exception as e:
        logger.error(f"Error in get_flood_months: {e}")
        return []