from datetime import datetime, timedelta
from re import search, sub, findall
from sys import argv, exc_info
from os import mkdir, makedirs
from os.path import exists, abspath
from traceback import format_exception

from ddtrace import tracer

import requests
import baseball


ALL_GAMES_URL = ('http://gdx.mlb.com/components/game/mlb/year_{year:04d}/'
                 'month_{month:02d}/day_{day:02d}/miniscoreboard.json')

GAME_URL_TEMPLATE = 'http://statsapi.mlb.com/api/v1.1/game/{game_pk}/feed/live'

HTML_INDEX_PAGE = (
    '<html>'
      '<head>'
      '<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/'
      'jquery.min.js"></script>'
        '<link rel="icon" type="image/png" href="baseball-fairy-161.png" />'
        '<meta name="viewport" content="width=device-width, initial-scale=0.35">'
        '<meta http-equiv="cache-control" content="no-cache">'
        '<meta http-equiv="refresh" content="45">'
        '<!-- Global site tag (gtag.js) - Google Analytics -->'
        '<script async src="https://www.googletagmanager.com/gtag/js'
        '?id=UA-108577160-1"></script>'
        '<script>'
            'var timeoutPeriod = 1000;'
            'var imageURI = "2017-10-21-NYY-HOU-1.svg";'
            'var x=0, y=0;'
            'var img = new Image();'
            'img.onload = function() {{'
                'var canvas = document.getElementById("x");'
                'var context = canvas.getContext("2d");'
                'context.drawImage(img, x, y);'
                'x+=20; y+=20;'
                'setTimeout(timedRefresh,timeoutPeriod);'
            '}};'
            'function timedRefresh() {{'
                'img.src = imageURI + "?d=" + Date.now();'
            '}}'
        '</script>'
        '<script>'
          'window.dataLayer = window.dataLayer || [];'
          'function gtag(){{dataLayer.push(arguments);}}'
          'gtag("js", new Date());'
          'gtag("config", "UA-108577160-1");'
        '</script>'
        '<title>Live Baseball Scorecards</title>'
      '</head>'
      '<body style="background-color:black;">'
        '<div id="header" style="width:1160px; margin:0 auto; '
        'text-align: center;">'
          '<img src="baseball-fairy-bat-250.png" height="250"><br />'
          '<font size="7" color="white">'
          'LiveBaseballScorecards.com'
          '</font><br />'
          '<font size="5" color="white">'
            'Contact us at '
            '<a href="mailto:livebaseballscorecards@gmail.com" '
            'style="color:lightblue">livebaseballscorecards@gmail.com</a>'
            '<br />'
            'For abbreviation definitions, hover your mouse over the scorecard text or just click <a style="color:lightblue" href="abbreviations.html">here</a>.'
            '<br /><br />'
          '<font size="6" color="white">Select a game</font>'
          '<br />'
          '<select name="away" id="away">'
            '<option value="">Away Team</option>'
            '<option value="ARI">Arizona Diamondbacks</option>'
            '<option value="ATL">Atlanta Braves</option>'
            '<option value="BAL">Baltimore Orioles,</option>'
            '<option value="BOS">Boston Red Sox</option>'
            '<option value="CHC">Chicago Cubs</option>'
            '<option value="CHW">Chicago White Sox</option>'
            '<option value="CIN">Cincinnati Reds</option>'
            '<option value="CLE">Cleveland Indians</option>'
            '<option value="COL">Colorado Rockies</option>'
            '<option value="DET">Detroit Tigers</option>'
            '<option value="HOU">Houston Astros</option>'
            '<option value="KC">Kansas City Royals</option>'
            '<option value="LAA">Los Angeles Angels</option>'
            '<option value="LAD">Los Angeles Dodgers</option>'
            '<option value="MIA">Miami Marlins</option>'
            '<option value="MIL">Milwaukee Brewers</option>'
            '<option value="MIN">Minnesota Twins</option>'
            '<option value="NYM">New York Mets</option>'
            '<option value="NYY">New York Yankees</option>'
            '<option value="OAK">Oakland A\'s</option>'
            '<option value="PHI">Philadephia Phillies</option>'
            '<option value="PIT">Pittsburgh Pirates</option>'
            '<option value="SEA">Seattle Mariners</option>'
            '<option value="SD">San Diego Padres</option>'
            '<option value="SF">San Francisco Giants</option>'
            '<option value="STL">St. Louis Cardinals</option>'
            '<option value="TB">Tampa Bay Rays</option>'
            '<option value="TEX">Texas Rangers</option>'
            '<option value="TOR">Toronto Blue Jays</option>'
            '<option value="WSH">Washington Nationals</option>'
          '</select>'
          '<font color="white">@</font>'
          '<select name="home" id="home">'
            '<option value="">Home Team</option>'
            '<option value="ARI">Arizona Diamondbacks</option>'
            '<option value="ATL">Atlanta Braves</option>'
            '<option value="BAL">Baltimore Orioles,</option>'
            '<option value="BOS">Boston Red Sox</option>'
            '<option value="CHC">Chicago Cubs</option>'
            '<option value="CHW">Chicago White Sox</option>'
            '<option value="CIN">Cincinnati Reds</option>'
            '<option value="CLE">Cleveland Indians</option>'
            '<option value="COL">Colorado Rockies</option>'
            '<option value="DET">Detroit Tigers</option>'
            '<option value="HOU">Houston Astros</option>'
            '<option value="KC">Kansas City Royals</option>'
            '<option value="LAA">Los Angeles Angels</option>'
            '<option value="LAD">Los Angeles Dodgers</option>'
            '<option value="MIA">Miami Marlins</option>'
            '<option value="MIL">Milwaukee Brewers</option>'
            '<option value="MIN">Minnesota Twins</option>'
            '<option value="NYM">New York Mets</option>'
            '<option value="NYY">New York Yankees</option>'
            '<option value="OAK">Oakland A\'s</option>'
            '<option value="PHI">Philadephia Phillies</option>'
            '<option value="PIT">Pittsburgh Pirates</option>'
            '<option value="SEA">Seattle Mariners</option>'
            '<option value="SD">San Diego Padres</option>'
            '<option value="SF">San Francisco Giants</option>'
            '<option value="STL">St. Louis Cardinals</option>'
            '<option value="TB">Tampa Bay Rays</option>'
            '<option value="TEX">Texas Rangers</option>'
            '<option value="TOR">Toronto Blue Jays</option>'
            '<option value="WSH">Washington Nationals</option>'
          '</select>'
          '<br />'
          '<br />'
          '<select name="month" id="month">'
            '<option value="01">January</option>'
            '<option value="02">February</option>'
            '<option value="03">March</option>'
            '<option value="04">April</option>'
            '<option value="05">May</option>'
            '<option value="06">June</option>'
            '<option value="07">July</option>'
            '<option value="08">August</option>'
            '<option value="09">September</option>'
            '<option value="10">October</option>'
            '<option value="11">November</option>'
            '<option value="12">December</option>'
          '</select>'
          '<select name="day" id="day">'
            '<option value="01">1</option>'
            '<option value="02">2</option>'
            '<option value="03">3</option>'
            '<option value="04">4</option>'
            '<option value="05">5</option>'
            '<option value="06">6</option>'
            '<option value="07">7</option>'
            '<option value="08">8</option>'
            '<option value="09">9</option>'
            '<option value="10">10</option>'
            '<option value="11">11</option>'
            '<option value="12">12</option>'
            '<option value="13">13</option>'
            '<option value="14">14</option>'
            '<option value="15">15</option>'
            '<option value="16">16</option>'
            '<option value="17">17</option>'
            '<option value="18">18</option>'
            '<option value="19">19</option>'
            '<option value="20">20</option>'
            '<option value="21">21</option>'
            '<option value="22">22</option>'
            '<option value="23">23</option>'
            '<option value="24">24</option>'
            '<option value="25">25</option>'
            '<option value="26">26</option>'
            '<option value="27">27</option>'
            '<option value="28">28</option>'
            '<option value="29">29</option>'
            '<option value="30">30</option>'
            '<option value="31">31</option>'
          '</select>'
          '<select name="year" id="year">'
            '<option value="2019">2019</option>'
            '<option value="2018">2018</option>'
            '<option value="2017">2017</option>'
            '<option value="2016">2016</option>'
            '<option value="2015">2015</option>'
            '<option value="2014">2014</option>'
            '<option value="2013">2013</option>'
            '<option value="2012">2012</option>'
            '<option value="2011">2011</option>'
            '<option value="2010">2010</option>'
            '<option value="2009">2009</option>'
            '<option value="2008">2008</option>'
          '</select>'
          '<br />'
          '<br />'
          '<font color="white">Game number: </font>'
          '<select name="game" id="game">'
            '<option value="1">1</option>'
            '<option value="2">2</option>'
          '</select>'
          '<br />'
          '<br />'
          '<script>'
            'function gotogame() {{'
              'window.location = "./" + document.getElementById("year").value +'
              ' "-" + document.getElementById("month").value + "-" +'
              ' document.getElementById("day").value + "-" +'
              ' document.getElementById("away").value + "-" +'
              ' document.getElementById("home").value + "-" +'
              ' document.getElementById("game").value + ".html";'
            '}}'
          '</script>'
          '<button onclick="gotogame()">Submit</button>'
          '<br /><br />'
          '<font size="6" color="white">Today\'s Games</font>'
        '</div>'
        '<br />'
        '<table cellpadding="10" style="width:1160px" align="center">'
        '{result_object_list_str}'
        '</table>'
        '<script>'
          'window.addEventListener("scroll", function(e) {{ '
            'localStorage.setItem("last_scroll", $(window).scrollTop()); '
          '}}); \n'
          'if (localStorage.getItem("last_scroll")) {{ '
            '$(window).scrollTop(localStorage.getItem("last_scroll")); '
          '}} '
          'document.getElementById("day").onchange = function() {{ '
            'localStorage.setItem("dayselecteditem", '
            'document.getElementById("day").value); '
          '}} \n'
          'if (localStorage.getItem("dayselecteditem")) {{ '
            'document.getElementById("day").value =  '
            'localStorage.getItem("dayselecteditem"); '
          '}} '
          'document.getElementById("month").onchange = function() {{ '
            'localStorage.setItem("monthselecteditem",  '
            'document.getElementById("month").value); '
          '}} \n'
          'if (localStorage.getItem("monthselecteditem")) {{ '
            'document.getElementById("month").value =  '
            'localStorage.getItem("monthselecteditem"); '
          '}} '
          'document.getElementById("year").onchange = function() {{ '
            'localStorage.setItem("yearselecteditem",  '
            'document.getElementById("year").value); '
          '}} \n'
          'if (localStorage.getItem("yearselecteditem")) {{ '
            'document.getElementById("year").value =  '
            'localStorage.getItem("yearselecteditem"); '
          '}} '
          'document.getElementById("game").onchange = function() {{ '
            'localStorage.setItem("gameselecteditem",  '
            'document.getElementById("game").value); '
          '}} \n'
          'if (localStorage.getItem("gameselecteditem")) {{ '
            'document.getElementById("game").value =  '
            'localStorage.getItem("gameselecteditem"); '
          '}} '
          'document.getElementById("away").onchange = function() {{ '
            'localStorage.setItem("awayselecteditem",  '
            'document.getElementById("away").value); '
          '}} \n'
          'if (localStorage.getItem("awayselecteditem")) {{ '
            'document.getElementById("away").value =  '
            'localStorage.getItem("awayselecteditem"); '
          '}} '
          'document.getElementById("home").onchange = function() {{ '
            'localStorage.setItem("homeselecteditem",  '
            'document.getElementById("home").value); '
          '}} \n'
          'if (localStorage.getItem("homeselecteditem")) {{ '
            'document.getElementById("home").value =  '
            'localStorage.getItem("homeselecteditem"); '
          '}} '
        '</script>'
      '</body>'
    '</html>'
)


OBJECT_ENTRY_TEMPLATE = (
    '<td valign="top"><div align="center">'
    '<a id="{game_id_str}">'
    '<font size="5"><a style="color:lightblue; text-decoration: none;" '
    'href="{game_id_str}.html">{title_str}</a></font>'
    '</div>'
    '<br />'
    '<div align="center">'
    '<a href="./{game_id_str}.html"><img width="520px" '
    'src="./{game_id_str}.svg" type="image/svg+xml"></a>'
    '</div>'
    '</td>'
)

MLB_URL_BASE_PATTERN = ('http://gd2.mlb.com/components/game/mlb/year_{year}/'
                        'month_{month}/day_{day}')

GET_TODAY_GAMES_USAGE_STR = (
    'Usage:\n'
    '  - ./get_today_games.py [OUTPUT DIRECTORY]\n'
)

def parse_name(batter_name):
    if search(r'\w\s+[A-Z]\.\s+', batter_name):
        batter_name = sub(r'\s[A-Z]\.\s+', ' ', batter_name)

    player_first_name, player_last_name = batter_name.split(' ', 1)

    return player_first_name, player_last_name

def set_player_list(team_dict, team):
    for _, this_player_dict in team_dict['players'].items():
        jersey_number = ''
        if 'jerseyNumber' in this_player_dict and this_player_dict.get('jerseyNumber'):
            if all([character in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
                    for character in this_player_dict.get('jerseyNumber')]):
                jersey_number = int(this_player_dict.get('jerseyNumber'))

        (first_name, last_name) = parse_name(
            this_player_dict['person']['fullName']
        )

        team.append(
            baseball.Player(
                last_name,
                first_name,
                this_player_dict['person']['id'],
                float(this_player_dict['seasonStats']['batting']['obp']),
                float(this_player_dict['seasonStats']['batting']['slg']),
                jersey_number
            )
        )

def initialize_team(team_gamedata_dict, team_livedata_dict):
    team = baseball.Team(
        team_gamedata_dict['name'],
        team_gamedata_dict['abbreviation']
    )

    set_player_list(team_livedata_dict, team)
    team.pitcher_list = [
        baseball.PlayerAppearance(
            team[team_livedata_dict['pitchers'][0]], 1, 1, 'Top', 1
        )
    ]

    for _, player_dict in team_livedata_dict['players'].items():
        if player_dict.get('battingOrder'):
            batting_order = int(player_dict['battingOrder'])
            position = player_dict['allPositions'][0]['code']

            if batting_order % 100 == 0:
                batting_index = int((batting_order / 100) - 1)
                team.batting_order_list_list[batting_index] = [
                    baseball.PlayerAppearance(
                        team[int(player_dict['person']['id'])],
                        position,
                        1,
                        'Top',
                        1
                    )
                ]

    return team

def initialize_game(this_game):
    away_team = initialize_team(
        this_game['gameData']['teams']['away'],
        this_game['liveData']['boxscore']['teams']['away']
    )

    home_team = initialize_team(
        this_game['gameData']['teams']['home'],
        this_game['liveData']['boxscore']['teams']['home']
    )

    location = '{}, {}, {}'.format(
        this_game['gameData']['venue']['name'],
        this_game['gameData']['venue']['location']['city'],
        this_game['gameData']['venue']['location']['stateAbbrev']
    )

    start_date = None
    for play_event in this_game['liveData']['plays']['allPlays'][0]['playEvents']:
        if play_event['details']['description'] == 'Status Change - In Progress':
            start_date = baseball.process_game_xml.get_datetime(
                play_event['startTime']
            )
            break

    end_date = baseball.process_game_xml.get_datetime(
        this_game['liveData']['plays']['allPlays'][-1]['about']['endTime']
    )

    if start_date:
        game_str = '{}-{}-{}-{}-{}{}'.format(
            start_date.year,
            start_date.month,
            start_date.day,
            away_team.abbreviation,
            home_team.abbreviation,
            this_game['gameData']['game']['id'][-2:]
        )
    else:
        game_str = '{}-{}{}'.format(
            away_team.abbreviation,
            home_team.abbreviation,
            this_game['gameData']['game']['id'][-2:]
        )

    game_obj = baseball.Game(
        home_team,
        away_team,
        location,
        game_str,
        start_date,
        end_date,
        None
    )

    return game_obj

def get_inning_dict_list(game_dict):
    inning_dict_list = []
    inning_num = 1
    inning_half = 'top'

    while True:
        play_dict_list = []
        for this_play_dict in game_dict['liveData']['plays']['allPlays']:
            if (this_play_dict['about']['inning'] == inning_num and
                    this_play_dict['about']['halfInning'] == inning_half):
                play_dict_list.append(this_play_dict)

        if play_dict_list and inning_half == 'top':
            inning_dict_list.append({'top': play_dict_list})
            inning_half = 'bottom'
        elif play_dict_list and inning_half == 'bottom':
            inning_dict_list[-1]['bottom'] = play_dict_list
            inning_num += 1
            inning_half = 'top'
        elif play_dict_list:
            raise Exception('Invalid inning half value')
        else:
            break

    return inning_dict_list

def process_pitch(event):
    pitch_description = event['details']['call']['description']
    if event['details'].get('type'):
        pitch_type = event['details']['type']['code']
    else:
        pitch_type = ''

    pitch_datetime = baseball.process_game_xml.get_datetime(event['startTime'])

    if (not event['pitchData']['coordinates'].get('x') or
            not event['pitchData']['coordinates'].get('y') or
            event['pitchData']['coordinates'].get('x') == 'None' or
            event['pitchData']['coordinates'].get('y') == 'None'):
        (pitch_x, pitch_y) = baseball.baseball_events.AUTOMATIC_BALL_POSITION
    else:
        pitch_x = float(event['pitchData']['coordinates'].get('x'))
        pitch_y = float(event['pitchData']['coordinates'].get('y'))

    pitch_position = (pitch_x, pitch_y)

    if event['pitchData'].get('startSpeed'):
        pitch_speed = float(event['pitchData'].get('startSpeed'))
    else:
        pitch_speed = None

    pitch_obj = baseball.baseball_events.Pitch(
        pitch_datetime,
        pitch_description,
        pitch_type,
        pitch_speed,
        pitch_position
    )

    return pitch_obj

def process_pickoff(event):
    pickoff_description = event['details'].get('description')
    pickoff_base = pickoff_description.split()[-1]

    if (pickoff_description.split()[1] == 'Attempt' or
            pickoff_description.split()[1] == 'Error'):
        pickoff_was_successful = False
    elif len(pickoff_description.split()) == 2:
        pickoff_was_successful = True
    else:
        raise ValueError('Bad Pickoff description.')

    pickoff_obj = baseball.baseball_events.Pickoff(
        pickoff_description,
        pickoff_base,
        pickoff_was_successful
    )

    return pickoff_obj

def process_plate_appearance(plate_appearance, inning_half_str, inning_num, next_batter_num, game_obj):
    event_list = []
    scoring_runners_list = []
    runners_batted_in_list = []
    steal_description = None

    old_flags = (False, False, False, None, None)
    for event in plate_appearance['playEvents']:
        if event['type'] == 'pitch':
            pitch_obj = process_pitch(event)
            event_list.append(pitch_obj)
            old_flags = (False, False, False, None, None)
        elif event['type'] == 'pickoff':
            pickoff_obj = process_pickoff(event)
            event_list.append(pickoff_obj)
            old_flags = (False, False, False, None, None)
        elif event['type'] == 'action':
            event_description = event['details']['description']
            event_summary = event['details'].get('event', '')
            event_datetime = baseball.process_game_xml.get_datetime(event['startTime'])

            (substitution_flag,
             switch_flag,
             steal_flag) = baseball.process_game_xml.get_sub_switch_steal_flags(event_summary,
                                                                                event_description)

            if substitution_flag:
                (substituting_team,
                 substitution_obj) = baseball.process_game_xml.parse_substitution(event_datetime,
                                                                                  event_description,
                                                                                  event_summary,
                                                                                  inning_half_str,
                                                                                  game_obj)

                event_list.append(substitution_obj)
                baseball.process_game_xml.process_substitution(substitution_obj, inning_num,
                                                               inning_half_str, next_batter_num,
                                                               substituting_team)

            elif switch_flag:
                (switch_obj,
                 switching_team) = baseball.process_game_xml.parse_switch_description(event_datetime,
                                                                                      event_description,
                                                                                      event_summary,
                                                                                      game_obj,
                                                                                      inning_half_str)

                event_list.append(switch_obj)
                baseball.process_game_xml.process_switch(switch_obj, inning_num, inning_half_str,
                                                         next_batter_num, switching_team)
            elif steal_flag:
                steal_description = event_description

            old_flags = (substitution_flag, switch_flag, steal_flag, event_description, event_summary)
        elif event['type'] == 'no_pitch':
            old_flags = (False, False, False, None, None)
        else:
            raise Exception('Invalid event type')

    for runner_event in plate_appearance['runners']:
        runner_id = int(runner_event['details']['runner']['id'])

        if runner_id in game_obj.away_team:
            runner = game_obj.away_team[runner_id]
        elif runner_id in game_obj.home_team:
            runner = game_obj.home_team[runner_id]
        else:
            raise ValueError('Runner ID not in player dict')

        start_base = runner_event['movement'].get('start') or ''
        end_base = runner_event['movement'].get('end', '') or ''
        run_description = runner_event['details'].get('event')
        runner_scored = (runner_event['movement'].get('end') == 'score')
        run_earned = runner_event['details'].get('earned')
        is_rbi = runner_event['details'].get('rbi')

        runner_advance_obj = baseball.baseball_events.RunnerAdvance(
            run_description,
            runner,
            start_base,
            end_base,
            runner_scored,
            run_earned,
            is_rbi
        )

        if runner_advance_obj.runner_scored:
            scoring_runners_list.append(runner_advance_obj.runner)

            if runner_advance_obj.is_rbi:
                runners_batted_in_list.append(runner_advance_obj.runner)

        event_list.append(runner_advance_obj)

    return event_list, scoring_runners_list, runners_batted_in_list

def process_at_bat(plate_appearance, event_list, game_obj, steal_description,
                   inning_half_str, inning_num, next_batter_num):
    (new_event_list,
     scoring_runners_list,
     runners_batted_in_list) = process_plate_appearance(plate_appearance,
                                                        inning_half_str,
                                                        inning_num,
                                                        next_batter_num,
                                                        game_obj)

    event_list += new_event_list
    if not plate_appearance['result'].get('description'):
        return None

    plate_appearance_desc = baseball.process_game_xml.fix_description(
        plate_appearance['result'].get('description')
    )

    pitcher_id = int(plate_appearance['matchup']['pitcher']['id'])
    inning_outs = int(plate_appearance['count']['outs'])

    out_runner_supplemental_list = None
    pitcher = None
    for this_team in [game_obj.home_team, game_obj.away_team]:
        if pitcher_id in this_team:
            pitcher = this_team[pitcher_id]
        elif steal_description:
            out_runner_supplemental_list = (
                baseball.PlateAppearance.get_out_runners_list(steal_description,
                                                              this_team)
            )

    if not pitcher:
        raise ValueError('Batter ID not in player_dict')

    batter_id = int(plate_appearance['matchup']['batter']['id'])
    if batter_id in game_obj.home_team:
        batter = game_obj.home_team[batter_id]
        batting_team = game_obj.home_team
    elif batter_id in game_obj.away_team:
        batter = game_obj.away_team[batter_id]
        batting_team = game_obj.away_team
    else:
        raise ValueError('Batter ID not in player_dict')

    start_datetime = baseball.process_game_xml.get_datetime(plate_appearance['about']['startTime'])
    end_datetime = baseball.process_game_xml.get_datetime(plate_appearance['about']['endTime'])
    plate_appearance_summary = plate_appearance['result']['event'].strip()

    plate_appearance_obj = baseball.PlateAppearance(start_datetime,
                                                    end_datetime,
                                                    batting_team,
                                                    plate_appearance_desc,
                                                    plate_appearance_summary,
                                                    pitcher,
                                                    batter,
                                                    inning_outs,
                                                    scoring_runners_list,
                                                    runners_batted_in_list,
                                                    event_list)

    if out_runner_supplemental_list:
        plate_appearance_obj.out_runners_list += out_runner_supplemental_list

    return plate_appearance_obj

def set_pitcher_wls_codes(game_dict, game):
    away_wls_dict = {
        x['person']['id']: x['stats']['pitching']['note'][1]
        for _, x in game_dict['liveData']['boxscore']['teams']['away']['players'].items()
        if x['stats']['pitching'].get('note')
    }

    home_wls_dict = {
        x['person']['id']: x['stats']['pitching']['note'][1]
        for _, x in game_dict['liveData']['boxscore']['teams']['home']['players'].items()
        if x['stats']['pitching'].get('note')
    }

    for pitcher_appearance in game.away_team.pitcher_list:
        pitcher_id = pitcher_appearance.player_obj.mlb_id
        if pitcher_id in away_wls_dict:
            pitcher_appearance.pitcher_credit_code = (
                away_wls_dict[pitcher_id]
            )
        else:
            pitcher_appearance.pitcher_credit_code = ''


    for pitcher_appearance in game.home_team.pitcher_list:
        pitcher_id = pitcher_appearance.player_obj.mlb_id
        if pitcher_id in home_wls_dict:
            pitcher_appearance.pitcher_credit_code = (
                home_wls_dict[pitcher_id]
            )
        else:
            pitcher_appearance.pitcher_credit_code = ''

def process_half_inning(plate_appearance_dict_list, inning_half_str, game_obj):
    if inning_half_str not in ('top', 'bottom'):
        raise ValueError('Invalid inning half str.')

    plate_appearance_list = []
    inning_num = len(game_obj.inning_list) + 1
    next_batter_num = 1
    for plate_appearance_dict in plate_appearance_dict_list:
        steal_description = None
        event_list = []
        plate_appearance_list.append(
            process_at_bat(
                plate_appearance_dict,
                event_list,
                game_obj,
                steal_description,
                inning_half_str,
                inning_num,
                next_batter_num
            )
        )

        next_batter_num += 1

    return plate_appearance_list

def process_inning(baseball_inning, game_obj):
    top_half_appearance_list = process_half_inning(
        baseball_inning['top'],
        'top',
        game_obj
    ) or []

    if baseball_inning.get('bottom'):
        bottom_half_appearance_list = process_half_inning(baseball_inning['bottom'],
                                                          'bottom',
                                                          game_obj)
    else:
        bottom_half_appearance_list = []

    if top_half_appearance_list and top_half_appearance_list[-1] is None:
        del top_half_appearance_list[-1]
    if bottom_half_appearance_list and bottom_half_appearance_list[-1] is None:
        del bottom_half_appearance_list[-1]

    this_inning_obj = baseball.Inning(top_half_appearance_list,
                                      bottom_half_appearance_list)

    return this_inning_obj

def set_game_inning_list(inning_dict_list, game_obj):
    for inning_index, inning_dict in enumerate(inning_dict_list):
        game_obj.inning_list.append(process_inning(inning_dict, game_obj))

def get_today_date_str(this_datetime):
    today_date_str = '{}-{}-{}'.format(this_datetime.year,
                                       str(this_datetime.month).zfill(2),
                                       str(this_datetime.day).zfill(2))

    return today_date_str

def get_object_html_str(game_html_id_list):
    object_html_str = ''
    for i, game_html_id in enumerate(game_html_id_list):
        game_id_element_list = game_html_id.split('-')
        title_str = '{} @ {} ({}-{}-{}, {})'.format(
            game_id_element_list[3],
            game_id_element_list[4],
            game_id_element_list[0],
            game_id_element_list[1],
            game_id_element_list[2],
            game_id_element_list[5]
        )

        if i % 2 == 0:
            object_html_str += '<tr>'

        object_html_str += OBJECT_ENTRY_TEMPLATE.format(
            title_str=title_str,
            game_id_str=game_html_id
        )

        if i % 2 == 1:
            object_html_str += '</tr>'

    return object_html_str

def write_games_for_date(this_datetime, output_dir):
    if not exists(output_dir):
        mkdir(output_dir)

    month = this_datetime.month
    day = this_datetime.day
    year = this_datetime.year
    all_games_dict = requests.get(ALL_GAMES_URL.format(month=month, day=day, year=year)).json()
    game_tuple_list = [(x['id'], x['game_pk']) for x in all_games_dict['data']['games']['game']]
    game_dict_list = [requests.get(GAME_URL_TEMPLATE.format(game_pk=game_pk)).json()
                      for _, game_pk in game_tuple_list]

    game_html_id_list = []
    for game_dict in game_dict_list:
        try:
            game = initialize_game(game_dict)
            set_game_inning_list(get_inning_dict_list(game_dict), game)
            set_pitcher_wls_codes(game_dict, game)
            game.set_batting_box_score_dict()
            game.set_pitching_box_score_dict()
            game.set_team_stats()
            game.set_gametimes()
            baseball.fetch_game.write_game_svg_and_html(game.game_date_str, game, output_dir)
            game_html_id_list.append(game.game_date_str)
        except Exception as e:
            print(game_dict['gameData']['game']['id'])
            print(e)
            print()

    object_html_str = get_object_html_str(game_html_id_list)
    output_html = HTML_INDEX_PAGE.format(result_object_list_str=object_html_str)
    if object_html_str or not exists(output_dir + '/index.html'):
        with open(output_dir + '/index.html', 'w', encoding='utf-8') as fh:
            fh.write(output_html)

def generate_today_game_svgs(output_dir):
    time_shift = timedelta(hours=11)
    today_datetime = datetime.utcnow() - time_shift
    write_games_for_date(today_datetime, output_dir)

if __name__ == '__main__':
    if len(argv) < 2:
        print(GET_TODAY_GAMES_USAGE_STR)
    else:
        generate_today_game_svgs(argv[1])