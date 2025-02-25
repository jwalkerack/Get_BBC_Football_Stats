from lambda_functions.football_extraction.Lambda_Function.extract_game_data import GetGameData
from lambda_functions.football_extraction.Lambda_Function.web_utils import Generate_Soup
from lambda_functions.football_extraction.StepsActionedByUser.SaveToDisk_interactions import save_match_to_file
from lambda_functions.football_extraction.StepsActionedByUser.flood_to_s3 import lambda_handler_flood
import logging

logger = logging.getLogger()

Actions = ['Return_One_Match_Save_To_File', 'NightUpdate', 'DeleteListOfIds', 'ReturnGane']
# Local testing
if __name__ == "__main__":
    Action = 'Return_One_Match_Save_To_File'
    if Action == 'Return_One_Match_Save_To_File':
        ## Testing Of Edge Cases
        pens = "https://www.bbc.co.uk/sport/football/live/cew5w91gy74t"
        awaypenmulti = "https://www.bbc.co.uk/sport/football/live/cde9e0n26kdt"
        ownGoals = "https://www.bbc.co.uk/sport/football/live/cdjd0k3e29xt"
        multiAss = "https://www.bbc.co.uk/sport/football/live/czdnpd6eyrgt"
        get_game_html = Generate_Soup(awaypenmulti)
        if get_game_html[1] == True:
            get_game_data = GetGameData(get_game_html[0],'TestingLeague','czdnpd6eyrgt')
            folderLocation = r"C:\Users\44756\Desktop\projects\DATA"
            save_match_to_file(get_game_data,'own1.json',folderLocation)
    elif Action == 'Flood_S3':
         test_event = {}  # Simulate an event
         response = lambda_handler_flood(test_event, None)







