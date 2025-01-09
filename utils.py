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


#### So What Needs to Be Done for the Games
#### You Could Take the Identifers

def Process_Data(matches):
    JsonTemplate = {}
    for m in matches:
        matchUrl = f"https://www.bbc.co.uk/sport/football/live/{m}#MatchStats"
        matchSoup = Generate_Soup(matchUrl)
        Row = []
        if matchSoup[1] is True:
            match = matchSoup[0]

            JsonTemplate[m] = {"played_on": get_match_played_on_date(match),
                                 "venue": get_venue(match),
                                 "attendance": get_attendance_value(match),
                                 "home_team": {
                                     "name": get_the_home_team_name(match),
                                     "score": get_home_score(match),
                                     "possession": (return_possesion(match)[0])
                                 },
                                 "away_team": {
                                     "name": get_the_away_team_name(match),
                                     "score": get_away_score(match),
                                     "possession": return_possesion(match)[1]
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