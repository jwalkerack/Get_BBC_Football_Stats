
from player_data_model import GeneratePlayerModelCompleted


def Generate_Soup(URL):
    import requests
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}
    from bs4 import BeautifulSoup as bs
    try:
        make_request = requests.get(URL, headers=headers)
        if make_request.status_code == 200:
            make_soup = [bs(make_request.text, "html.parser"), True]
        else:
            make_soup = [bs(make_request.text, "html.parser"), make_request.status_code]
        return make_soup
    except requests.exceptions.RequestException as e:
        make_soup = [0, False]
        return make_soup

        print(f'Error: {e}')


def extract_match_identifiers1(soup_object):
    # Find all <li> elements with the 'data-tipo-topic-id' attribute
    elements = soup_object.find_all('li', attrs={"data-tipo-topic-id": True})
    identifiers = [element['data-tipo-topic-id'] for element in elements]

    return identifiers


def get_match_played_on_date(soup):
    playedOn = soup.find('time', class_='ssrcss-1hjuztf-Date ejf0oom1').text
    return playedOn


def get_venue(soup):
    venue_element = soup.find('div', class_='ssrcss-mz82d9-Venue')
    return venue_element.text.split("Venue:")[-1].strip() if venue_element else None


def get_attendance_value(soup):
    attendance_element = soup.find('div', class_='ssrcss-13d7g0c-AttendanceValue')
    return attendance_element.text.split("Attendance:")[-1].strip() if attendance_element else None


def get_the_home_team_name(soup):
    home_team_container = soup.find('div', class_='ssrcss-bon2fo-WithInlineFallback-TeamHome')
    home_team_name = home_team_container.find('span', class_='ssrcss-1p14tic-DesktopValue').text
    return home_team_name


def get_home_score(soup):
    home_score_element = soup.find('div', class_='ssrcss-qsbptj-HomeScore')
    return home_score_element.text.strip() if home_score_element else None


def return_possesion(soup):
    # <div aria-hidden="true" class=" emwj40c3"><div class="ssrcss-yq8av3-KeyColourLabelWrapper emwj40c2"><div class="ssrcss-1jegqx9-KeyColourBox e157ldzt0"></div><div class="ssrcss-157qu0j-KeyLabel emwj40c1">CEL</div></div><div class="ssrcss-1hrh75t-Value emwj40c0">70.4%</div></div>
    all_values = soup.find_all("div", class_=["ssrcss-1xfttdr-Value emwj40c0", "ssrcss-1hrh75t-Value emwj40c0"])
    if len(all_values) == 2:
        home_possession = all_values[0].text
        away_possession = all_values[1].text
    else:
        home_possession = None
        away_possession = None
    return [home_possession, away_possession]


def get_the_away_team_name(soup):
    away_team_container = soup.find('div', class_='ssrcss-nvj22c-WithInlineFallback-TeamAway')
    away_team_name = away_team_container.find('span', class_='ssrcss-1p14tic-DesktopValue').text

    return away_team_name


def get_away_score(soup):
    away_score_element = soup.find('div', class_='ssrcss-fri5a2-AwayScore')
    return away_score_element.text.strip() if away_score_element else None
def get_formations(soup):
    homeForm = soup.find('p',attrs={'data-testid': 'match-lineups-home-formation'},class_='ssrcss-rqdoa8-Detail e1qxd70s5')
    awayForm = soup.find('p',attrs={'data-testid': 'match-lineups-away-formation'},class_='ssrcss-rqdoa8-Detail e1qxd70s5')
    return [homeForm.text if homeForm else None ,awayForm.text if awayForm else None]

def get_managers(soup):
    awayMan = soup.find('p',attrs={'data-testid': 'match-lineups-away-manager'},class_='ssrcss-rqdoa8-Detail e1qxd70s5')
    homeMan = soup.find('p',attrs={'data-testid': 'match-lineups-home-manager'},class_='ssrcss-rqdoa8-Detail e1qxd70s5')
    return [homeMan.text if homeMan else None,awayMan.text if awayMan else None ]

#### So What Needs to Be Done for the Games
#### You Could Take the Identifers

def extract_key_events(soup, event_type_class):
    import re
    """
    Args:
        soup (BeautifulSoup): The BeautifulSoup object containing the parsed HTML.
        event_type_class (str): The class identifier for the event container (e.g., 'KeyEventsHome' or 'KeyEventsAway').

    Returns:
        dict: A dictionary containing the team name and a list of events with details.
    """
    result = {'events': []}

    # Locate the main container for key events based on the event type class
    key_events_div = soup.find('div', class_=re.compile(f".*{event_type_class}.*"))
    if not key_events_div:
        print(f"Key events container with class '{event_type_class}' not found.")
        return result

    # Extract the team name from the visually hidden heading
    #team_heading = key_events_div.find('h4', class_='ssrcss-3t9f3z-Heading e10rt3ze0')
    #if team_heading:
        #result['team'] = team_heading.get_text(strip=True)
    #else:
        #print("Team name not found.")

    # Find all list items representing events
    event_items = key_events_div.find_all('li', class_=re.compile(".*StyledAction.*"))
    for item in event_items:
        event = {
            'player': '',
            'event_type': '',
            'details': '',
            'time': ''
        }
        # Extract player name from the span with role="text"
        player_span = item.find('span', role='text')
        if player_span:
            # Remove any HTML comments or extra spaces
            player_name = player_span.get_text(strip=True)
            event['player'] = player_name
        else:
            print("Player name not found for an event.")
            continue  # Skip this event if player name is missing

        # Extract the visually hidden text that describes the event
        hidden_span = item.find('span', class_='visually-hidden ssrcss-1f39n02-VisuallyHidden e16en2lz0')
        if hidden_span:
            hidden_text = hidden_span.get_text(separator=', ', strip=True)
            # Determine the event type and details
            if "Goal" in hidden_text:
                event['event_type'] = 'Goal'
                # Extract goal times using regex
                goals = re.findall(r'Goal (\d+)(?: minutes(?: plus (\d+))?)?', hidden_text)
                goal_times = []
                for goal in goals:
                    minute = goal[0]
                    extra = goal[1] if goal[1] else None
                    if extra:
                        goal_times.append(f"{minute}' +{extra}")
                    else:
                        goal_times.append(f"{minute}'")
                event['details'] = goal_times
            elif "Red Card" in hidden_text:
                event['event_type'] = 'Red Card'
                # Extract the minute of the red card
                red_card = re.search(r'Red Card (\d+) minutes', hidden_text)
                if red_card:
                    event['time'] = f"{red_card.group(1)}'"
            elif "Yellow Card" in hidden_text:
                event['event_type'] = 'Yellow Card'
                # Extract the minute of the yellow card
                yellow_card = re.search(r'Yellow Card (\d+) minutes', hidden_text)
                if yellow_card:
                    event['time'] = f"{yellow_card.group(1)}'"
            # Add more event types as needed
            else:
                event['event_type'] = 'Other'
                event['details'] = hidden_text
        else:
            # Fallback: Extract event details from the visible spans
            time_spans = item.find_all('span', class_='ssrcss-1t9po6g-TextBlock e102yuqa0')
            times = []
            for ts in time_spans:
                time_text = ts.get_text(strip=True)
                # Clean the time text by removing parentheses and commas
                time_text = re.sub(r'[(),]', '', time_text)
                times.append(time_text)
            event['details'] = times

            # Attempt to infer event type based on presence of certain elements
            # For example, presence of a card image can indicate a card event
            card_img = item.find('img', alt=True)
            if card_img:
                alt_text = card_img.get('alt').lower()
                if 'red card' in alt_text:
                    event['event_type'] = 'Red Card'
                elif 'yellow card' in alt_text:
                    event['event_type'] = 'Yellow Card'
                else:
                    event['event_type'] = 'Card'
            else:
                event['event_type'] = 'Unknown'

        result['events'].append(event)
    return result



def Process_Data(matches,leagueName):
    JsonTemplate = {}
    for m in matches:
        matchUrl = f"https://www.bbc.co.uk/sport/football/live/{m}#MatchStats"
        matchSoup = Generate_Soup(matchUrl)
        Row = []
        if matchSoup[1] is True:
            match = matchSoup[0]
            getTheFormations = get_formations(match)
            getTheManagers = get_managers(match)
            buildPlayerModel  = GeneratePlayerModelCompleted(match)
            HomePlayers =  buildPlayerModel[0]
            AwayPlayers = buildPlayerModel[1]
            #getAwayEvents = extract_key_events(match, 'KeyEventsAway')
            JsonTemplate[m] = {"played_on": get_match_played_on_date(match),
                                 "venue": get_venue(match),
                               "League_Name": leagueName,
                                 "attendance": get_attendance_value(match),
                                 "home_team": {
                                     "formation" : getTheFormations[0],
                                     "manager" : getTheManagers[0],
                                     "name": get_the_home_team_name(match),
                                     "score": get_home_score(match),
                                     "possession": (return_possesion(match)[0]),
                                     "players" : HomePlayers
                                 },
                                 "away_team": {
                                     "formation": getTheFormations[1],
                                     "manager": getTheManagers[1],
                                     "name": get_the_away_team_name(match),
                                     "score": get_away_score(match),
                                     "possession": return_possesion(match)[1],
                                     "players": AwayPlayers
                                 }}
    return JsonTemplate



def filter_past_or_current_months(games_dict):
    from datetime import datetime, date
    """
    Returns a new dict with only entries whose YYYY-MM
    is <= the current year-month (today).
    """
    # Use the actual current date
    today = date.today()
    # Get the start of the current month (day=1)
    current_month_start = date(today.year, today.month, 1)

    filtered = {}
    for label, val in games_dict.items():
        # 'val' is typically a string like '2024-08'
        dt = datetime.strptime(val, '%Y-%m')
        dt_month_start = date(dt.year, dt.month, 1)

        # Keep if the month-year is <= today’s month-year
        if dt_month_start <= current_month_start:
            filtered[label] = val

    return filtered

def flatten_match_data(DataDict):
    table = []
    for matchKey in DataDict:
        matchObject = DataDict[matchKey]
        Row = [matchKey,
               matchObject["played_on"],
               matchObject["venue"],
               matchObject["attendance"],
               matchObject["home_team"]["name"],
               matchObject["home_team"]["score"],
               matchObject["home_team"]["possession"],
               matchObject["away_team"]["name"],
               matchObject["away_team"]["score"],
               matchObject["away_team"]["possession"]]
        table.append(Row)
    return table

def extract_key_events(soup, event_type_class):
    import re
    """
    Extracts key events from the provided BeautifulSoup object.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object containing the parsed HTML.
        event_type_class (str): The class identifier for the event container (e.g., 'KeyEventsHome' or 'KeyEventsAway').

    Returns:
        dict: A dictionary containing the team name and a list of events with details.
    """
    # Initialize the result dictionary
    result = {
        #'team': '',
        'events': []
    }

    # Locate the main container for key events based on the event type class
    key_events_div = soup.find('div', class_=re.compile(f".*{event_type_class}.*"))
    if not key_events_div:
        print(f"Key events container with class '{event_type_class}' not found.")
        return result

    # Extract the team name from the visually hidden heading
    #team_heading = key_events_div.find('h4', class_='ssrcss-3t9f3z-Heading e10rt3ze0')
    #if team_heading:
        #result['team'] = team_heading.get_text(strip=True)
    #else:
        #print("Team name not found.")

    # Find all list items representing events
    event_items = key_events_div.find_all('li', class_=re.compile(".*StyledAction.*"))
    for item in event_items:
        event = {
            'player': '',
            'event_type': '',
            'details': '',
            'time': ''
        }

        # Extract player name from the span with role="text"
        player_span = item.find('span', role='text')
        if player_span:
            # Remove any HTML comments or extra spaces
            player_name = player_span.get_text(strip=True)
            event['player'] = player_name
        else:
            print("Player name not found for an event.")
            continue  # Skip this event if player name is missing

        # Extract the visually hidden text that describes the event
        hidden_span = item.find('span', class_='visually-hidden ssrcss-1f39n02-VisuallyHidden e16en2lz0')
        if hidden_span:
            hidden_text = hidden_span.get_text(separator=', ', strip=True)
            # Determine the event type and details
            if "Goal" in hidden_text:
                event['event_type'] = 'Goal'
                # Extract goal times using regex
                goals = re.findall(r'Goal (\d+)(?: minutes(?: plus (\d+))?)?', hidden_text)
                goal_times = []
                for goal in goals:
                    minute = goal[0]
                    extra = goal[1] if goal[1] else None
                    if extra:
                        goal_times.append(f"{minute}' +{extra}")
                    else:
                        goal_times.append(f"{minute}'")
                event['details'] = goal_times
            elif "Red Card" in hidden_text:
                event['event_type'] = 'Red Card'
                # Extract the minute of the red card
                red_card = re.search(r'Red Card (\d+) minutes', hidden_text)
                if red_card:
                    event['time'] = f"{red_card.group(1)}'"
            elif "Yellow Card" in hidden_text:
                event['event_type'] = 'Yellow Card'
                # Extract the minute of the yellow card
                yellow_card = re.search(r'Yellow Card (\d+) minutes', hidden_text)
                if yellow_card:
                    event['time'] = f"{yellow_card.group(1)}'"
            # Add more event types as needed
            else:
                event['event_type'] = 'Other'
                event['details'] = hidden_text
        else:
            # Fallback: Extract event details from the visible spans
            time_spans = item.find_all('span', class_='ssrcss-1t9po6g-TextBlock e102yuqa0')
            times = []
            for ts in time_spans:
                time_text = ts.get_text(strip=True)
                # Clean the time text by removing parentheses and commas
                time_text = re.sub(r'[(),]', '', time_text)
                times.append(time_text)
            event['details'] = times

            # Attempt to infer event type based on presence of certain elements
            # For example, presence of a card image can indicate a card event
            card_img = item.find('img', alt=True)
            if card_img:
                alt_text = card_img.get('alt').lower()
                if 'red card' in alt_text:
                    event['event_type'] = 'Red Card'
                elif 'yellow card' in alt_text:
                    event['event_type'] = 'Yellow Card'
                else:
                    event['event_type'] = 'Card'
            else:
                event['event_type'] = 'Unknown'

        result['events'].append(event)

    return result

def pass_data_to_bucket(AA,AAS,jsonFileName,jsonData):
    import boto3
    s3_client = boto3.client(
    "s3",
    region_name="us-east-1",
    aws_access_key_id=AA,
    aws_secret_access_key=AAS)
    object_folder = "Raw/"
    object_key = object_folder + jsonFileName
    bucket_name = "datapulledraw"
    try:
        response = s3_client.put_object(Bucket=bucket_name,Key=object_key,Body=jsonData,ContentType="application/json")
    except:
        pass
    return response

