import json
import os
from typing import Optional
import requests
import datetime
import time as t
from mcb.utils import convert_time
import logging
logger = logging.getLogger(__name__)


URL="http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard"

# def get_game(team_name):
#     for i in range(5):
#         try:
#             res = requests.get(URL)
#             res = res.json()
#             for g in res['events']:
#                 if team_name in g['shortName']:
#                     info = g['competitions'][0]
#                     game = {'name': g['shortName'], 'date': g['date'],
#                             'hometeam': info['competitors'][0]['team']['abbreviation'], 'homeid': info['competitors'][0]['id'], 'homescore': int(info['competitors'][0]['score']),
#                             'awayteam': info['competitors'][1]['team']['abbreviation'], 'awayid': info['competitors'][1]['id'], 'awayscore': int(info['competitors'][1]['score']),
#                             'down': info.get('situation', {}).get('shortDownDistanceText'), 'spot': info.get('situation', {}).get('possessionText'),
#                             'time': info['status']['displayClock'], 'quarter': info['status']['period'], 'over': info['status']['type']['completed'],
#                             'redzone': info.get('situation', {}).get('isRedZone'), 'possession': info.get('situation', {}).get('possession'), 'state': info['status']['type']['state']}
#                     return game
#         except requests.exceptions.RequestException as e:
#             print("Error encountered getting game info, can't hit ESPN api, retrying")
#             if i < 4:
#                 t.sleep(1)
#                 continue
#             else:
#                 print("Can't hit ESPN api after multiple retries, dying ", e)
#         except Exception as e:
#             print("something bad?", e)

def get_all_games():
    # for i in range(5):
    try:
        res = requests.get(URL)
        res = res.json()
        games = []
        # i = 0
        for g in res['events']:
            info = g['competitions'][0]
            game = {'name': g['shortName'], 'date': g['date'],
                    'hometeam': info['competitors'][0]['team']['abbreviation'], 'homeid': info['competitors'][0]['id'], 'homescore': int(info['competitors'][0]['score']),
                    'awayteam': info['competitors'][1]['team']['abbreviation'], 'awayid': info['competitors'][1]['id'], 'awayscore': int(info['competitors'][1]['score']),
                    # 'down': info.get('situation', {}).get('shortDownDistanceText'), 'spot': info.get('situation', {}).get('possessionText'),
                    'time': info['status']['displayClock'], 'period': info['status']['period'], 'over': info['status']['type']['completed'],
                    # 'redzone': info.get('situation', {}).get('isRedZone'), 'possession': info.get('situation', {}).get('possession'),
                     'state': info['status']['type']['state']}

            games.append(game)
            # i += 1
        return games
    except requests.exceptions.RequestException as e:
        logger.warning("Error encountered getting game info, can't hit ESPN api, retrying")
        # if i < 4:
        #     t.sleep(1)
        #     continue
        # else:
        #     print("Can't hit ESPN api after multiple retries, dying ", e)
    except Exception as e:
        logger.error("Unknown exception", exc_info=True)


def download_all_logos(api_data_path:Optional[str] = None) -> None:
    """
    Download all the logos
    api_data_path: None to grab data from API.
        If not None, must be a path to a file containing API data in JSON format, eg the sample file provided.
    """
    # Scan data for logos
    logos = []
    api_data = None
    if api_data_path is None:
        try:
            api_data = requests.get(URL)
            api_data = api_data.json()
        except requests.exceptions.RequestException as e:
            logger.warning("Error encountered getting game info, can't hit ESPN api, retrying")
        except Exception as e:
            logger.error("Unknown exception", exc_info=True)
    else:
        try:
            with open(api_data_path, 'r') as data_file:
                api_data = json.load(data_file)
        except Exception as e:
            logger.error("Failed to load data file:", exc_info=True)

    if not api_data is None:
        for event in api_data['events']:
            for competition in event['competitions']:
                for competitor in competition['competitors']:
                    team = competitor['team']
                    abbrev = team["abbreviation"]
                    logo_url = team["logo"]
                    logos.append((abbrev,logo_url))

    dest_dir = os.path.join(os.path.dirname(__file__), '..', 'logos')
    logger.info("Downloading %d logos to %s."%(len(logos), dest_dir))
    for abbrev,logo_url in logos:
        logo_data = requests.get(logo_url)
        dest_file = os.path.join(dest_dir, "%s.png"%abbrev)
        with open(dest_file, 'wb') as f:
            f.write(logo_data.content)
        logger.info("Saved %s"%abbrev)

# def which_game(games, fav_team):
#     # check for fav team first
#     for game in games:
#         if games[game]['hometeam'] == fav_team or games[game]['awayteam'] == fav_team:
#             return games[game]
#     # games should be sorted by date, earliest to latest
#     for game in games:
#         # testing purposes
#         # if games[game]['state'] == 'post':
#         #     return games[game]
#         if games[game]['state'] == 'in':
#             return games[game]
#         if games[game]['state'] == 'pre':
#             return games[game]
#         if games[game]['state'] == 'post':
#             return games[game]
#     return None

# def is_playoffs():
#     try:
#         res = requests.get(URL)
#         res = res.json()
#         return res['season']['type'] == 3
#     except requests.exceptions.RequestException:
#         print("Error encountered getting game info, can't hit ESPN api")
#     except Exception as e:
#         print("something bad?", e)

