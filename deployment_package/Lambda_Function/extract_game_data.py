import re
import unicodedata
from .extract_player import generate_player_dictionaries
import logging
logger = logging.getLogger()
# ----------------------------------------------
# UTF-8 Encoding Fix
# ----------------------------------------------
def clean_text(text):
    """Normalize text encoding to ensure correct special characters (UTF-8)."""
    if text:
        text = unicodedata.normalize("NFKC", text).strip()
        return text.encode("utf-8").decode("utf-8")  #  Forces correct UTF-8 representation
    return None


# ----------------------------------------------
#  1. Core Data Extraction Functions
# ----------------------------------------------


def extract_match_identifiers(soup_object):
    """Extracts match identifiers from the soup object."""
    try:
        elements = soup_object.find_all('li', attrs={"data-tipo-topic-id": True})
        if not elements:
            logger.warning("No match identifiers found in the soup object.")
        else:
            logger.info([element['data-tipo-topic-id'] for element in elements])
        return [element['data-tipo-topic-id'] for element in elements]
    except Exception as e:
        logger.error(f"Unexpected error in extract_match_identifiers: {e}")
        return []





def get_match_played_on_date(soup):
    """Extract the match played-on date."""
    played_on = soup.find('time', class_='ssrcss-1hjuztf-Date ejf0oom1')
    return clean_text(played_on.text) if played_on else None


def get_venue(soup):
    """Extract the match venue."""
    venue_element = soup.find('div', class_='ssrcss-mz82d9-Venue')
    return clean_text(venue_element.text.split("Venue:")[-1].strip()) if venue_element else None


def get_attendance(soup):
    """Extract attendance numbers from the match."""
    attendance_element = soup.find('div', class_='ssrcss-13d7g0c-AttendanceValue')
    return clean_text(attendance_element.text.split("Attendance:")[-1].strip()) if attendance_element else None


def get_home_team_name(soup):
    """Extracts the home team's name, handling missing elements safely."""
    home_team_container = soup.find('div', class_='ssrcss-bon2fo-WithInlineFallback-TeamHome')

    # Check if the container exists
    if home_team_container:
        home_team_name = home_team_container.find('span', class_='ssrcss-1p14tic-DesktopValue')
        if home_team_name:
            return home_team_name.text  # Keep the original extraction logic

    return None


def get_home_score(soup):
    """Extract home team's score."""
    home_score_element = soup.find('div', class_='ssrcss-qsbptj-HomeScore')

    return clean_text(home_score_element.text) if home_score_element else None

def get_away_score(soup):
    """Extract away team's score."""
    away_score_element = soup.find('div', class_='ssrcss-fri5a2-AwayScore')
    return clean_text(away_score_element.text) if away_score_element else None


def get_away_team_name(soup):
    """Extract the away team name."""
    away_team_container = soup.find('div', class_='ssrcss-nvj22c-WithInlineFallback-TeamAway')
    if away_team_container:
        away_team_name = away_team_container.find('span', class_='ssrcss-1p14tic-DesktopValue')
        if away_team_name:
            return away_team_name.text  # Keep the original extraction logic

    return None




def get_possession(soup):
    """Extract possession statistics."""
    all_values = soup.find_all("div", class_=["ssrcss-1xfttdr-Value emwj40c0", "ssrcss-1hrh75t-Value emwj40c0"])
    home_possession = clean_text(all_values[0].text) if len(all_values) >= 2 else None
    away_possession = clean_text(all_values[1].text) if len(all_values) >= 2 else None
    return home_possession, away_possession


# ----------------------------------------------
# 2. Player and Event Data Extraction
# ----------------------------------------------
def extract_goal_events(soup, event_type_class):
    """Extract goal events for home and away teams."""
    goals_data = {}
    key_events_div = soup.find('div', class_=re.compile(f".*{event_type_class}.*"))

    if not key_events_div:
        return goals_data

    event_items = key_events_div.find_all('li', class_=re.compile(".*StyledAction.*"))

    for item in event_items:
        player_span = item.find('span', role='text')
        if not player_span:
            continue

        player_name = clean_text(player_span.get_text(strip=True))
        hidden_span = item.find('span', class_='visually-hidden ssrcss-1f39n02-VisuallyHidden e16en2lz0')

        if hidden_span:
            hidden_text = hidden_span.get_text(separator=', ', strip=True)
            if "Goal" in hidden_text:
                goal_times = re.findall(r'(\d+)(?: minutes(?: plus (\d+))?)?', hidden_text)
                goals_data[player_name] = [f"{minute}' +{extra}" if extra else f"{minute}'" for minute, extra in
                                           goal_times]

    return goals_data


def extract_players_and_assists(soup, searchString):
    """Extract assists and associated times from the match report."""
    container = soup.find('div', class_=re.compile(searchString))
    if not container:
        return {}

    player_data = {}
    spans = container.find_all('span', class_='visually-hidden')
    if spans:
        spans[0].extract()

    text = container.get_text(strip=True)
    entries = text.split(',')

    for entry in entries:
        if '(' in entry and ')' in entry:
            player_info, time_info = entry.split('(')
            player_name = clean_text(player_info.strip())
            assist_time = time_info.strip(')').strip()

            if player_name not in player_data:
                player_data[player_name] = []

            player_data[player_name].append(assist_time)

    return player_data

def get_formations(soup):
    homeForm = soup.find('p',attrs={'data-testid': 'match-lineups-home-formation'},class_='ssrcss-rqdoa8-Detail e1qxd70s5')
    awayForm = soup.find('p',attrs={'data-testid': 'match-lineups-away-formation'},class_='ssrcss-rqdoa8-Detail e1qxd70s5')
    return [homeForm.text if homeForm else None ,awayForm.text if awayForm else None]

def get_managers(soup):
    awayMan = soup.find('p',attrs={'data-testid': 'match-lineups-away-manager'},class_='ssrcss-rqdoa8-Detail e1qxd70s5')
    homeMan = soup.find('p',attrs={'data-testid': 'match-lineups-home-manager'},class_='ssrcss-rqdoa8-Detail e1qxd70s5')
    return [
        clean_text(homeMan.text) if homeMan else None,
        clean_text(awayMan.text) if awayMan else None
    ]
# ----------------------------------------------
# 3. Master Function: GetGameData
# ----------------------------------------------
def GetGameData(soup,league,bbcKey):
    """Extracts all key match details from the given BeautifulSoup object, including players."""
    if not soup:
        return {"error": "Invalid Soup Object"}

    home_possession, away_possession = get_possession(soup)
    home_formation, away_formation = get_formations(soup)
    home_manager, away_manager = get_managers(soup)

    # Extract players (this includes lineup, subs, goals, and assists)
    player_data = generate_player_dictionaries(soup)

    match_data = {
        "match_id": bbcKey,
        "played_on": get_match_played_on_date(soup),
        "venue": get_venue(soup),
        "attendance": get_attendance(soup),
        "League_Name": league,
        "home_team": {
            "formation" : home_formation,
            "manager": home_manager,
            "name": get_home_team_name(soup),
            "score": get_home_score(soup),
            "possession": home_possession,
            "players": player_data[0]  # Home team players with goals, assists, subs
        },
        "away_team": {
            "formation": away_formation,
            "manager": away_manager,
            "name": get_away_team_name(soup),
            "score": get_away_score(soup),
            "possession": away_possession,
            "players": player_data[1]  # Away team players with goals, assists, subs
        }
    }

    return match_data

