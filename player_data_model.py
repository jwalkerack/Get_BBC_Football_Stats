import re


def Generate_Soup(URL):
    import requests
    from bs4 import BeautifulSoup as bs
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}

    try:
        make_request = requests.get(URL, headers=headers)
        if make_request.status_code == 200:
            # Set the encoding explicitly
            make_request.encoding = 'utf-8'  # Ensure proper character encoding
            make_soup = [bs(make_request.text, "html.parser"), True]
        else:
            make_request.encoding = 'utf-8'  # Still handle encoding even if there's an error
            make_soup = [bs(make_request.text, "html.parser"), make_request.status_code]
        return make_soup
    except requests.exceptions.RequestException as e:
        make_soup = [0, False]
        print(f'Error: {e}')
        return make_soup


def extract_players_and_assists(soup, searchString):
    container = soup.find('div', class_=re.compile(searchString))
    if not container:
        return {}

    # Initialize the result dictionary
    player_data = {}

    # Extract player information
    spans = container.find_all('span', class_='visually-hidden')
    if spans:
        # Remove the visually hidden span if present
        spans[0].extract()

    # Extract text for players and their assist times
    text = container.get_text(strip=True)
    entries = text.split(',')

    for entry in entries:
        if '(' in entry and ')' in entry:
            player_info, time_info = entry.split('(')
            player_name = player_info.strip()
            assist_time = time_info.strip(')').strip()

            if player_name not in player_data:
                player_data[player_name] = []

            player_data[player_name].append(assist_time)

    return player_data


def extract_goal_events(soup, event_type_class):
    import re
    """
    Args:
        soup (BeautifulSoup): The BeautifulSoup object containing the parsed HTML.
        event_type_class (str): The class identifier for the event container (e.g., 'KeyEventsHome' or 'KeyEventsAway').

    Returns:
        dict: A dictionary where the key is the player's name and the value is a list of goal times.
    """
    goals_data = {}

    # Locate the main container for key events based on the event type class
    key_events_div = soup.find('div', class_=re.compile(f".*{event_type_class}.*"))
    if not key_events_div:
        print(f"Key events container with class '{event_type_class}' not found.")
        return goals_data

    # Find all list items representing events
    event_items = key_events_div.find_all('li', class_=re.compile(".*StyledAction.*"))
    for item in event_items:
        # Extract player name from the span with role="text"
        player_span = item.find('span', role='text')
        if not player_span:
            continue  # Skip if no player name is found

        player_name = player_span.get_text(strip=True)

        # Extract the visually hidden text that describes the event
        hidden_span = item.find('span', class_='visually-hidden ssrcss-1f39n02-VisuallyHidden e16en2lz0')
        if hidden_span:
            hidden_text = hidden_span.get_text(separator=', ', strip=True)
            # Check if the event is a goal
            if "Goal" in hidden_text:
                # Extract goal times using regex
                goals = re.findall(r'(\d+)(?: minutes(?: plus (\d+))?)?', hidden_text)
                goal_times = []
                for goal in goals:
                    minute = goal[0]
                    extra = goal[1] if goal[1] else None
                    if extra:
                        goal_times.append(f"{minute}' +{extra}")
                    else:
                        goal_times.append(f"{minute}'")

                # Add the player and their goals to the dictionary
                if player_name not in goals_data:
                    goals_data[player_name] = []
                goals_data[player_name].extend(goal_times)

    return goals_data


def extract_player_data(player_list):
    """
    Extracts player information from the given player list, including substitutions, cards, minutes played,
    and who replaced a player.
    """
    players_data = []
    substitution_map = {}
    replaced_by_map = {}
    total_minutes = 98  # Default match length

    for player_item in player_list.find_all("li", {"data-testid": "player-list-item"}):
        # Extract basic player details
        player_name, player_number = extract_basic_details(player_item)

        # Extract substitution details
        substitutions, was_substituted = extract_substitution_details(player_item)

        # Extract yellow card details
        yellow_card_count, yellow_card_minutes = extract_card_details(player_item, "yellowcard")

        # Extract red card details
        red_card_count, red_card_minutes = extract_card_details(player_item, "red-card")

        # Create the base player data
        player_data = create_base_player_data(
            player_name,
            player_number,
            was_substituted,
            yellow_card_count,
            yellow_card_minutes,
            red_card_count,
            red_card_minutes,
            total_minutes,
        )

        # Handle substitutions
        if substitutions:
            player_data["WasSubstituted"] = True
            player_data["IsSubstitute"] = False
            player_data["MinutesPlayed"] = substitutions[0]["SubMinute"]

            current_subbed_for = player_name
            for sub in substitutions:
                sub_name = sub["SubName"]
                sub_minute = sub["SubMinute"]

                replaced_by_map[current_subbed_for] = sub_name

                # Add substitute to the players data
                players_data.append(create_substitute_data(sub_name, sub_minute, total_minutes))

                current_subbed_for = sub_name

        players_data.append(player_data)

    # Post-process replacements
    post_process_replacements(players_data, replaced_by_map)

    return players_data


def extract_basic_details(player_item):
    """Extracts basic details like name and number."""
    player_name = player_item.find("span", class_="ssrcss-15c46u3-PlayerName").get_text(strip=True)
    player_number = player_item.find("span", class_="ssrcss-1b0eh30-PlayerNumber").get_text(strip=True).split(",")[0]
    return player_name, player_number


def extract_substitution_details(player_item):
    """Extracts substitution details."""
    substitutes_span = player_item.find("span", class_="ssrcss-1y48ox6-Substitutes")
    is_substitute = substitutes_span is not None
    was_substituted = False
    substitutions = []

    if is_substitute:
        for substitution in substitutes_span.find_all("span", {"aria-hidden": "true"}):
            sub_details = substitution.get_text(strip=True)
            sub_name, sub_minute = sub_details.rsplit(" ", 1)
            substitutions.append({"SubName": sub_name.strip(","), "SubMinute": int(sub_minute.strip("'"))})
            was_substituted = True

    return substitutions, was_substituted


def extract_card_details(player_item, card_type):
    """Extracts card details (yellow or red)."""
    card_elements = player_item.find_all("span", class_="ssrcss-limr09-Wrapper")
    card_count = 0
    card_minutes = []

    for card_element in card_elements:
        img = card_element.find("img", class_="ssrcss-oqfhdy-CardImage")
        if img and card_type in img["src"]:
            card_count += 1
            minute_span = card_element.find("span", {"aria-hidden": "true"})
            if minute_span:
                card_minutes.append(minute_span.get_text(strip=True))

    return card_count, card_minutes


def create_base_player_data(player_name, player_number, was_substituted, yellow_card_count, yellow_card_minutes,
                            red_card_count, red_card_minutes, total_minutes):
    """Creates the base data structure for a player."""
    return {
        "PlayerName": player_name,
        "PlayerNumber": player_number,
        "IsStarted": True,
        "IsSubstitute": False,
        "WasSubstituted": was_substituted,
        "ReplacedBy": None,
        "SubMinute": None,
        "YellowCards": yellow_card_count,
        "YellowCardMinutes": yellow_card_minutes,
        "RedCards": red_card_count,
        "RedCardMinutes": red_card_minutes,
        "MinutesPlayed": total_minutes,
    }


def create_substitute_data(sub_name, sub_minute, total_minutes):
    """Creates the data structure for a substitute player."""
    return {
        "PlayerName": sub_name,
        "PlayerNumber": None,
        "IsStarted": False,
        "IsSubstitute": True,
        "WasSubstituted": False,
        "ReplacedBy": None,
        "SubMinute": sub_minute,
        "YellowCards": 0,
        "YellowCardMinutes": [],
        "RedCards": 0,
        "RedCardMinutes": [],
        "MinutesPlayed": abs(total_minutes - sub_minute),
    }


def post_process_replacements(players_data, replaced_by_map):
    """Post-processes the replacements to assign who replaced whom."""
    for player in players_data:
        if player["PlayerName"] in replaced_by_map:
            player["ReplacedBy"] = replaced_by_map[player["PlayerName"]]


def merge_of_players_starting_subs(Starts, Subs):
    merged_players = {}
    for player in Starts:
        if player["PlayerName"] not in merged_players:
            merged_players[player["PlayerName"]] = {'ShirtNumber': player["PlayerNumber"],
                                                    'StartedGame': player["IsStarted"],
                                                    'IsSubstitute': player["IsSubstitute"],
                                                    'WasSubstituted': player["WasSubstituted"],
                                                    'ReplacedBy': player["ReplacedBy"],
                                                    'YellowCards': player["YellowCards"],
                                                    'YellowCardMinutes': player["YellowCardMinutes"],
                                                    'RedCards': player["RedCards"],
                                                    'RedCardMinutes': player["RedCardMinutes"],
                                                    'MinutesPlayed': player["MinutesPlayed"]}

    for player in Subs:
        if player["PlayerName"] not in merged_players:
            merged_players[player["PlayerName"]] = {'ShirtNumber': player["PlayerNumber"],
                                                    'StartedGame': False,
                                                    'IsSubstitute': False,
                                                    'WasSubstituted': False,
                                                    'ReplacedBy': None,
                                                    'YellowCards': None,
                                                    'YellowCardMinutes': None,
                                                    'RedCards': None,
                                                    'RedCardMinutes': None,
                                                    'MinutesPlayed': 0}
        else:
            merged_players[player['PlayerName']]['ShirtNumber'] = player['PlayerNumber']
            merged_players[player['PlayerName']]['YellowCards'] = player['YellowCards']
            merged_players[player['PlayerName']]['YellowCardMinutes'] = player['YellowCardMinutes']
            merged_players[player['PlayerName']]['RedCards'] = player['RedCards']
            merged_players[player['PlayerName']]['RedCardMinutes'] = player['RedCardMinutes']
    return merged_players


def Generate_players_model(soup):
    import re
    ContainerFind = soup.find('div', class_="ssrcss-17r0mao-GridContainer-LineupsGridContainer e977btc2")
    find_Teams = ContainerFind.find_all("div", class_=re.compile(".*TeamPlayers e1qxd70s1*"))
    find_Subs = ContainerFind.find_all("section", class_=re.compile(".*SubstitutesSection e977btc4*"))

    ## Home Team

    HomeTeam = extract_player_data(find_Teams[0])
    HomeSubs = extract_player_data(find_Subs[0])
    HomePlayers = merge_of_players_starting_subs(HomeTeam, HomeSubs)

    ## Away Team

    AwayTeam = extract_player_data(find_Teams[1])
    AwaySubs = extract_player_data(find_Subs[1])
    AwayPlayers = merge_of_players_starting_subs(AwayTeam, AwaySubs)

    return [HomePlayers, AwayPlayers]


def GeneratePlayerModelCompleted(soup):
    playerDataModel = Generate_players_model(soup)
    HomeGoals = extract_goal_events(soup, 'KeyEventsHome')
    HomeAssists = extract_players_and_assists(soup, ".*GroupedHomeEvent e1ojeme81*")
    ## Away
    AwayGoals = extract_goal_events(soup, 'KeyEventsAway')
    AwayAssists = extract_players_and_assists(soup, ".*GroupedAwayEvent e1ojeme80*")
    addGoals = AddGoalsData(HomeGoals, AwayGoals, playerDataModel)
    addAssists = AddAssistData(HomeAssists, AwayAssists, addGoals)
    return addAssists


def AddGoalsData(HomeGoals, AwayGoals, PlayerModel):
    for homeScorer in HomeGoals:
        if homeScorer in PlayerModel[0]:
            PlayerModel[0][homeScorer]['Goals'] = HomeGoals[homeScorer]

    for AwayScorer in AwayGoals:
        if AwayScorer in PlayerModel[1]:
            PlayerModel[1][AwayScorer]['Goals'] = AwayGoals[AwayScorer]
    return PlayerModel


def AddAssistData(HomeAssists, AwayAssists, PlayerModel):
    for HomeAssist in HomeAssists:
        if HomeAssist in PlayerModel[0]:
            PlayerModel[0][HomeAssist]['Assists'] = HomeAssists[HomeAssist]

    for AwayAssist in AwayAssists:
        if AwayAssist in PlayerModel[1]:
            PlayerModel[1][AwayAssist]['Goals'] = AwayAssists[AwayAssist]
    return PlayerModel
