import concurrent.futures
import os
from lambda_functions.football_extraction.Lambda_Function.web_utils import Generate_Soup
from lambda_functions.football_extraction.Lambda_Function.S3_utilities import get_json_from_s3 , update_json_in_s3,save_match_data_to_s3
from lambda_functions.football_extraction.Lambda_Function.general_utils import generate_file_name
from lambda_functions.football_extraction.Lambda_Function.extract_game_data import GetGameData , extract_match_identifiers
from config_Dev import S3_BUCKET ,S3_FILE_KEY,S3_FOLDER


import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def process_games_for_months(months_to_process, leagues):
    """
    Processes match data for a list of given months.

    Args:
        months_to_process (list): A list of YYYY-MM strings representing months to process.
        leagues (dict): Dictionary of leagues and their URLs.
    """
    for stringYearMonth in months_to_process:
        for league, league_url in leagues.items():
            try:
                leagueYearMonth = f"{league_url}/{stringYearMonth}?filter=results"
                makeCallLeagueYearMonth = Generate_Soup(leagueYearMonth)

                if not makeCallLeagueYearMonth[1]:
                    logger.error(f"Failed to fetch league data: {leagueYearMonth}")
                    continue

                id_dictionary = get_json_from_s3(S3_BUCKET,S3_FILE_KEY)
                if not isinstance(id_dictionary, dict):
                    logger.error("Failed to fetch valid match identifiers from S3.")
                    continue

                JSON_LIST = []
                MATCH_LIST = []
                ERROR_LIST = []
                returnLeagueYearMonthIds = extract_match_identifiers(makeCallLeagueYearMonth[0])
                logger.info(f"Match IDs to be processed: {returnLeagueYearMonthIds}")

                for page in returnLeagueYearMonthIds:
                    logger.info(f"Failed to save match data to S3 for {page}")
                    if page not in id_dictionary["identifiers"]:
                        matchURL = f"https://www.bbc.co.uk/sport/football/live/{page}"
                        callMatch = Generate_Soup(matchURL)

                        if callMatch[1]:
                            logger.info(f"Processing match: {matchURL}")
                            match_data = GetGameData(callMatch[0], league, page)
                            logger.info(f"Match Data: {match_data}")
                            JSON_LIST.append(match_data)
                            MATCH_LIST.append(page)
                        else:
                            logger.warning(f"Failed to fetch match data: {matchURL}")
                            ERROR_LIST.append(page)

                # 🔹 Prevent Saving Empty Files 🔹
                if JSON_LIST:
                    filename = generate_file_name(league, stringYearMonth)
                    saveToBucket = save_match_data_to_s3(JSON_LIST, filename,S3_BUCKET,S3_FOLDER)

                    if not saveToBucket:
                        logger.error(f"Failed to save match data to S3 for {filename}")
                    else:
                        logger.info(f"SaveWorked {filename}")
                else:
                    logger.info(f"No match data to save for {league} {stringYearMonth}, skipping S3 save.")

                # 🔹 Only Update Identifiers If We Actually Processed Matches 🔹
                if MATCH_LIST:
                    for m in MATCH_LIST:
                        id_dictionary["identifiers"][m] = {"status": "uploaded"}
                if ERROR_LIST:
                    for m1 in ERROR_LIST:
                        id_dictionary["identifiers"][m1] = {"status": "error", "version": 2}


                success = update_json_in_s3(id_dictionary,S3_BUCKET,S3_FILE_KEY)
                if not success:
                    logger.error("Failed to update match identifiers in S3.")
                else:
                    logger.info(f"No new match IDs processed for {league} {stringYearMonth}, skipping identifier update.")

            except Exception as e:
                logger.error(f"Unexpected error in process_games_for_months: {e}")


def process_games_for_months_TD(months_to_process, leagues):

    """
    Processes match data for a list of given months using threading.
    """
    for stringYearMonth in months_to_process:
        for league, league_url in leagues.items():
            try:
                leagueYearMonth = f"{league_url}/{stringYearMonth}?filter=results"
                makeCallLeagueYearMonth = Generate_Soup(leagueYearMonth)

                if not makeCallLeagueYearMonth[1]:
                    logger.error(f"Failed to fetch league data: {leagueYearMonth}")
                    continue

                id_dictionary = get_json_from_s3(S3_BUCKET,S3_FILE_KEY)
                if not isinstance(id_dictionary, dict):
                    logger.error("Failed to fetch valid match identifiers from S3.")
                    continue

                JSON_LIST = []
                MATCH_LIST = []
                ERROR_LIST = []
                returnLeagueYearMonthIds = extract_match_identifiers(makeCallLeagueYearMonth[0])

                with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                    future_to_page = {
                        executor.submit(process_match_TD, page, league, id_dictionary): page
                        for page in returnLeagueYearMonthIds
                    }

                    for future in concurrent.futures.as_completed(future_to_page):
                        try:
                            match_data, page = future.result()
                            if match_data:
                                JSON_LIST.append(match_data)
                                MATCH_LIST.append(page)
                            else:
                                ERROR_LIST.append(page)
                        except Exception as e:
                            logger.error(f"Error processing match {future_to_page[future]}: {e}")
                            ERROR_LIST.append(future_to_page[future])

                filename = generate_file_name(league, stringYearMonth)
                saveToBucket = save_match_data_to_s3(JSON_LIST, filename,S3_BUCKET,S3_FOLDER)

                if not saveToBucket:
                    logger.error(f"Failed to save match data to S3 for {filename}")

                for m in MATCH_LIST:
                    id_dictionary["identifiers"][m] = {"status": "uploaded"}
                for m1 in ERROR_LIST:
                    id_dictionary["identifiers"][m1] = {"status": "error"}

                success = update_json_in_s3(id_dictionary,S3_BUCKET,S3_FILE_KEY)
                if not success:
                    logger.error("Failed to update match identifiers in S3.")

            except Exception as e:
                logger.error(f"Unexpected error in process_games_for_months_TD: {e}")

def process_match_TD(page, league, id_dictionary):
    """Fetch match data and return results for a single match.

    Args:
        page (str): The match ID.
        league (str): The league name.
        id_dictionary (dict): The JSON dictionary tracking processed matches.

    Returns:
        tuple: (match_data, page) if successful, (None, None) otherwise.
    """
    try:
        if page in id_dictionary["identifiers"]:
            return None, None

        matchURL = f"https://www.bbc.co.uk/sport/football/live/{page}"
        callMatch = Generate_Soup(matchURL)

        if callMatch[1]:
            logger.info(f"Processing match: {matchURL}")
            match_data = GetGameData(callMatch[0], league, page)
            return match_data, page

        logger.warning(f"Failed to fetch match data: {matchURL}")
        return None, None

    except Exception as e:
        logger.error(f"Unexpected error in process_match_TD: {e}")
        return None, None
