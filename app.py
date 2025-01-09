import streamlit as st
import json
import pandas as pd
from datetime import datetime

from reference import leagues , GamesPlayed

from utils import Generate_Soup , extract_match_identifiers1 , Process_Data , flatten_match_data ,filter_past_or_current_months

# Example data references
# Replace these with your actual modules or dictionaries.


# Example utility functions
# Replace these with your actual functions from utils.py, etc.



# CALLBACKS
# -----------------------------------------------------------------------------
def on_make_selections():
    st.session_state["selection_state"] = 1
    st.session_state["info_msg"] = ""

def on_confirm_selections():
    # Only confirm if valid league & month chosen
    if st.session_state.get("valid_league_chosen", False) and st.session_state.get("valid_month_chosen", False):
        st.session_state["selection_state"] = 2
        st.session_state["info_msg"] = "Selections confirmed. You can now get the game count below."
    else:
        st.session_state["info_msg"] = "Please select a league and a date range before confirming."

def on_change_selections():
    # Wipe out existing data so that downloads are removed, etc.
    st.session_state["selection_state"] = 1
    st.session_state["processed_data"] = None
    st.session_state["game_count"] = 0
    st.session_state["identifiers"] = []
    st.session_state["info_msg"] = ""

def on_get_game_count(url):
    soup_list = Generate_Soup(url)
    if soup_list[1] == True:
        # success
        identifiers = extract_match_identifiers1(soup_list[0])
        st.session_state["game_count"] = len(identifiers)
        st.session_state["identifiers"] = identifiers
        st.session_state["info_msg"] = f"There are **{len(identifiers)}** games available."
    else:
        st.session_state["info_msg"] = f"Failed to retrieve data. Status: {soup_list[1]}"

def on_process_games():
    if st.session_state["game_count"] > 0:
        identifiers = st.session_state["identifiers"]
        processed_data = Process_Data(identifiers)
        st.session_state["processed_data"] = processed_data
        st.session_state["info_msg"] = "Processing complete! You can now download the data below."
    else:
        st.session_state["info_msg"] = "No games to process."

# -----------------------------------------------------------------------------
# MAIN APP
# -----------------------------------------------------------------------------
def main():
    # -------------------------------------------------------------------------
    # Initialize session state variables
    # -------------------------------------------------------------------------
    if "selection_state" not in st.session_state:
        st.session_state["selection_state"] = 0  # 0=brand new; 1=selecting; 2=confirmed
    if "game_count" not in st.session_state:
        st.session_state["game_count"] = 0
    if "identifiers" not in st.session_state:
        st.session_state["identifiers"] = []
    if "processed_data" not in st.session_state:
        st.session_state["processed_data"] = None
    if "info_msg" not in st.session_state:
        st.session_state["info_msg"] = ""
    if "valid_league_chosen" not in st.session_state:
        st.session_state["valid_league_chosen"] = False
    if "valid_month_chosen" not in st.session_state:
        st.session_state["valid_month_chosen"] = False

    # Title & Overview
    filteredGames = filter_past_or_current_months(GamesPlayed)
    st.title("Football Questions")
    st.markdown(
        """
        Hey Max and Lucy, I hope you had a good holiday. I made this little game for you.
        Look forward to seeing you and hearing the answers  **Uncle Jack**
        -Use the Buttons below to Select Leagues and Months to Download the Data that will give you answers
        - Can you please tell me me who plays at **London Stadium**
        - Can you please tell me which **English Championship** Team plays at "Turf Moor".
        - Can you please tell me what the score in the  **Scottish league One** when  played **Kelty Hearts** played **Dumbarton** on  November 2024
        - In August 2024, which game had the most goals in the **English Championship**
        """
    )

    # -------------------------------------------------------------------------
    # TOP ROW: Make / Confirm / Change Selections
    # -------------------------------------------------------------------------
    col1, col2, col3 = st.columns(3)

    with col1:
        st.button(
            "Start",
            on_click=on_make_selections,
            disabled=(st.session_state["selection_state"] != 0),
        )

    with col2:
        st.button(
            "Confirm",
            on_click=on_confirm_selections,
            disabled=(st.session_state["selection_state"] != 1),
        )

    with col3:
        st.button(
            "Change",
            on_click=on_change_selections,
            disabled=(st.session_state["selection_state"] != 2),
        )

    # Display info messages to user, if any
    if st.session_state["info_msg"]:
        st.info(st.session_state["info_msg"])

    # -------------------------------------------------------------------------
    # League/Month Selections (enabled if selection_state==1)
    # -------------------------------------------------------------------------
    disabled_dropdowns = not (st.session_state["selection_state"] == 1)

    league_choice = st.selectbox(
        "Select the league",
        list(leagues.keys()),
        disabled=disabled_dropdowns,
    )
    date_choice = st.selectbox(
        "Select the date range",
        list(filteredGames.keys()),
        disabled=disabled_dropdowns,
    )

    # Check if user actually picked something
    st.session_state["valid_league_chosen"] = league_choice is not None
    st.session_state["valid_month_chosen"] = date_choice is not None

    league_value = leagues[league_choice]
    month_value = filteredGames[date_choice]
    final_url = f"{league_value}/{month_value}?filter=results"

    # -------------------------------------------------------------------------
    # BOTTOM ROW: Get Game Count & Process Games (enabled if selection_state==2)
    # -------------------------------------------------------------------------
    if st.session_state["selection_state"] == 2:
        colA, colB = st.columns(2)
        with colA:
            st.button(
                "Get Game Count",
                on_click=on_get_game_count,
                args=(final_url,),  # pass final_url to the callback
            )
        with colB:
            # Only enable "Process Games" if game_count > 0
            st.button(
                "Process Games",
                on_click=on_process_games,
                disabled=(st.session_state["game_count"] == 0),
            )

    # -------------------------------------------------------------------------
    # DOWNLOAD SECTION: only appears if processed_data is not None
    # -------------------------------------------------------------------------
    if st.session_state["processed_data"] is not None:
        # Convert processed data to JSON/CSV
        json_data = json.dumps(st.session_state["processed_data"], indent=2)

        columns = [
            "bbcMatchId",
            "played_on",
            "venue",
            "attendance",
            "home_team_name",
            "home_team_score",
            "home_team_possession",
            "away_team_name",
            "away_team_score",
            "away_team_possession",
        ]
        flattened_data = flatten_match_data(st.session_state["processed_data"])
        df = pd.DataFrame(flattened_data, columns=columns)
        csv_data = df.to_csv(index=False)

        # File naming
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        league_part = league_choice.replace(" ", "-")
        date_part = date_choice.replace(" ", "-")
        json_filename = f"{league_part}_{date_part}_{timestamp}_games.json"
        csv_filename = f"{league_part}_{date_part}_{timestamp}_games.csv"

        colJson, colCsv = st.columns(2)
        with colJson:
            st.download_button(
                label="Download as JSON",
                data=json_data,
                file_name=json_filename,
                mime="application/json",
            )
        with colCsv:
            st.download_button(
                label="Download as CSV",
                data=csv_data,
                file_name=csv_filename,
                mime="text/csv",
            )

if __name__ == "__main__":
    main()