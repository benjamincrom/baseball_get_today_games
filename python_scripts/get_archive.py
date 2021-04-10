import datetime

from pathlib import Path
from sys import exc_info
from traceback import format_exception

import requests
import wget

MLB_TEAM_CODE_DICT = {'LAA': 'ana',
                      'SEA': 'sea',
                      'BAL': 'bal',
                      'CLE': 'cle',
                      'CIN': 'cin',
                      'NYM': 'nyn',
                      'COL': 'col',
                      'LAD': 'lan',
                      'DET': 'det',
                      'TOR': 'tor',
                      'HOU': 'hou',
                      'OAK': 'oak',
                      'MIA': 'mia',
                      'ATL': 'atl',
                      'MIL': 'mil',
                      'CHC': 'chn',
                      'MIN': 'min',
                      'KC': 'kca',
                      'NYY': 'nya',
                      'TEX': 'tex',
                      'PHI': 'phi',
                      'WSH': 'was',
                      'PIT': 'pit',
                      'STL': 'sln',
                      'SD':  'sdn',
                      'ARI': 'ari',
                      'SF':  'sfn',
                      'CHW': 'cha',
                      'TB':  'tba',
                      'BOS': 'bos'}

ALL_GAMES_URL = ('http://gdx.mlb.com/components/game/mlb/year_{year:02d}/'
                 'month_{month:02d}/day_{day:02d}/miniscoreboard.json')

MLB_URL_PATTERN = ('http://gd2.mlb.com/components/game/mlb/year_{year:04d}/'
                   'month_{month:02d}/day_{day:02d}/gid_{game_id}/')

GAME_URL_2020_TEMPLATE = ('http://statsapi.mlb.com/api/v1.1/game/{game_pk}'
                          '/feed/live')

BOXSCORE_SUFFIX = 'boxscore.xml'
PLAYERS_SUFFIX = 'players.xml'
INNING_SUFFIX = 'inning/inning_all.xml'

def get_archive_2019(this_date, filehandle):
    month = this_date.month
    day = this_date.day
    year = this_date.year
    try:
        all_games_dict = requests.get(
            ALL_GAMES_URL.format(month=month, day=day, year=year)
        ).json()

        game_id_list = [
            game_dict['id'].replace('-', '_').replace('/', '_')
            for game_dict in all_games_dict['data']['games'].get('game', [])
        ]
    except:
        exc_type, exc_value, exc_traceback = exc_info()
        lines = format_exception(exc_type, exc_value, exc_traceback)
        exception_str = ' '.join(lines)
        filehandle.write('{} {}\n\n'.format(str(this_date),
                                            exception_str))

        return

    for game_id in game_id_list:
        full_path = "{:04d}/month_{:02d}/day_{:02d}/gid_{}/".format(
            year, month, day, game_id
        )

        Path(full_path + 'inning/').mkdir(parents=True, exist_ok=True)

        url_prefix = MLB_URL_PATTERN.format(
            year=year, month=month, day=day, game_id=game_id,
        )

        try:
            boxscore_file = Path(full_path + BOXSCORE_SUFFIX)
            if not boxscore_file.exists():
                wget.download(url_prefix + BOXSCORE_SUFFIX, full_path)

            players_file = Path(full_path + PLAYERS_SUFFIX)
            if not players_file.exists():
                wget.download(url_prefix + PLAYERS_SUFFIX, full_path)

            inning_file = Path(full_path + INNING_SUFFIX)
            if not inning_file.exists():
                wget.download(url_prefix + INNING_SUFFIX, full_path + 'inning/')
        except:
            exc_type, exc_value, exc_traceback = exc_info()
            lines = format_exception(exc_type, exc_value, exc_traceback)
            exception_str = ' '.join(lines)
            filehandle.write('{} {} {}\n\n'.format(str(this_date),
                                                   url_prefix,
                                                   exception_str))

def get_archive_2020(this_date, filehandle):
    month = this_date.month
    day = this_date.day
    year = this_date.year
    try:
        all_games_dict = requests.get(
            ALL_GAMES_URL.format(month=month, day=day, year=year)
        ).json()

        game_tuple_list = [
            (x['id'], x['game_pk'])
            for x in all_games_dict['data']['games'].get('game', [])
        ]
    except:
        exc_type, exc_value, exc_traceback = exc_info()
        lines = format_exception(exc_type, exc_value, exc_traceback)
        exception_str = ' '.join(lines)
        filehandle.write('{} {}\n\n'.format(str(this_date),
                                            exception_str))

        return

    for formatted_id, game_pk in game_tuple_list:
        url = GAME_URL_2020_TEMPLATE.format(game_pk=game_pk)
        game_id = formatted_id.replace('-', '_').replace('/', '_')
        full_path = "{:02d}/month_{:02d}/day_{:02d}/gid_{}/".format(
            year, month, day, game_id
        )

        Path(full_path).mkdir(parents=True, exist_ok=True)
        try:
            live_file = Path(full_path + 'live')
            if not live_file.exists():
                wget.download(url, full_path)
        except:
            exc_type, exc_value, exc_traceback = exc_info()
            lines = format_exception(exc_type, exc_value, exc_traceback)
            exception_str = ' '.join(lines)
            filehandle.write('{} {} {}\n\n'.format(str(this_date),
                                                   url,
                                                   exception_str))

if __name__ == '__main__':
    start_date = datetime.datetime(2021, 4, 1, 0, 0)
    end_date = datetime.datetime(2021, 4, 1, 0, 0)

    fh = open('output_log.txt', 'w')
    current_date = start_date
    while current_date <= end_date:
        if current_date.year < 2020:
            get_archive_2019(current_date, fh)
        else:
            get_archive_2020(current_date, fh)

        current_date = current_date + datetime.timedelta(days=1)
