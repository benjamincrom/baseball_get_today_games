import datetime

from pathlib import Path

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

MLB_URL_PATTERN = ('http://gd2.mlb.com/components/game/mlb/year_{year}/'
                   'month_{month}/day_{day}/gid_{year}_{month}_{day}_'
                   '{away_mlb_code}mlb_{home_mlb_code}mlb_{game_number}/')

BOXSCORE_SUFFIX = 'boxscore.xml'
PLAYERS_SUFFIX = 'players.xml'
INNING_SUFFIX = 'inning/inning_all.xml'

THIS_YEAR = 2018

with open('file_list.txt') as fh:
    rough_name_list = fh.readlines()

name_list = [x.strip()[:-4] for x in rough_name_list
             if len(x.strip()) > 15 and x.strip()[-4:] != 'html']


this_date = datetime.datetime(2018, 1, 1, 0, 0)
while this_date.year < 2020:
    for name in name_list:
        year, month, day, away_code, home_code, game_number = name.split('-')
        if (this_date.year == int(year) and this_date.month == int(month) and
                this_date.day == int(day)):
            away_mlb_code = MLB_TEAM_CODE_DICT[away_code]
            home_mlb_code = MLB_TEAM_CODE_DICT[home_code]

            dir_name = 'gid_{}_{}_{}_{}mlb_{}mlb_{}'.format(
                year, month, day, away_mlb_code, home_mlb_code, game_number
            )

            full_path = "{}/month_{}/day_{}/{}/".format(
                year, month, day, dir_name
            )

            Path(full_path + 'inning/').mkdir(parents=True, exist_ok=True)

            url_prefix = MLB_URL_PATTERN.format(
                year=year, month=month, day=day, away_mlb_code=away_mlb_code,
                home_mlb_code=home_mlb_code, game_number=game_number
            )

            wget.download(url_prefix + BOXSCORE_SUFFIX, full_path)
            wget.download(url_prefix + PLAYERS_SUFFIX, full_path)
            wget.download(url_prefix + INNING_SUFFIX, full_path + 'inning/')

    this_date = this_date + datetime.timedelta(days=1)
