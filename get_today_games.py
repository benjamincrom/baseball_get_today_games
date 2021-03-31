from datetime import datetime, timedelta
from os import mkdir, makedirs
from os.path import exists, abspath
from re import findall
from sys import argv, exc_info
from traceback import format_exception

from requests import get
from ddtrace import tracer

from baseball import (get_game_from_url, write_game_svg_and_html,
                      MLB_TEAM_CODE_DICT)


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


def get_page(this_datetime):
    page = get(
        MLB_URL_BASE_PATTERN.format(year=this_datetime.year,
                                    month=str(this_datetime.month).zfill(2),
                                    day=str(this_datetime.day).zfill(2))
    )

    return page

def get_today_date_str(this_datetime):
    today_date_str = '{}-{}-{}'.format(this_datetime.year,
                                       str(this_datetime.month).zfill(2),
                                       str(this_datetime.day).zfill(2))

    return today_date_str

def get_generated_html_id_list(game_id_list, today_date_str, output_dir):
    if not exists(output_dir):
        makedirs(output_dir)

    output_path = abspath(output_dir)
    game_html_id_list = []

    for game_id in game_id_list:
        away_mlb_code = game_id.split('_')[-3][:3]
        home_mlb_code = game_id.split('_')[-2][:3]
        game_num_str = game_id.split('_')[-1]

        if (away_mlb_code in MLB_TEAM_CODE_DICT.values() and
                home_mlb_code in MLB_TEAM_CODE_DICT.values()):
            away_code = [key for key, val in MLB_TEAM_CODE_DICT.items()
                         if val == away_mlb_code][0]
            home_code = [key for key, val in MLB_TEAM_CODE_DICT.items()
                         if val == home_mlb_code][0]

            try:
                game_id, game = get_game_from_url(today_date_str,
                                                  away_code,
                                                  home_code,
                                                  game_num_str)

                if game:
                    write_game_svg_and_html(game_id, game, output_path)
                    game_html_id_list.append(
                        '{}-{}-{}-{}'.format(today_date_str,
                                             away_code,
                                             home_code,
                                             game_num_str)
                    )
            except:
                exc_type, exc_value, exc_traceback = exc_info()
                lines = format_exception(exc_type, exc_value, exc_traceback)
                exception_str = ' '.join(lines)
                print('{} {} {}'.format(datetime.utcnow(), game_id, exception_str))

    return game_html_id_list

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

def generate_game_svgs_for_datetime(this_datetime, output_dir):
    if not exists(output_dir):
        mkdir(output_dir)

    today_date_str = get_today_date_str(this_datetime)
    page = get_page(this_datetime)

    game_id_list = findall(r'>\s*(gid\_\w+)/<', page.text)
    game_html_id_list = get_generated_html_id_list(game_id_list,
                                                   today_date_str,
                                                   output_dir)

    object_html_str = get_object_html_str(game_html_id_list)
    output_html = HTML_INDEX_PAGE.format(result_object_list_str=object_html_str)
    if object_html_str or not exists(output_dir + '/index.html'):
        with open(output_dir + '/index.html', 'w', encoding='utf-8') as fh:
            fh.write(output_html)

@tracer.wrap(service='get-todays-games')
def generate_today_game_svgs(output_dir):
    time_shift = timedelta(hours=11)
    today_datetime = datetime.utcnow() - time_shift
    generate_game_svgs_for_datetime(today_datetime, output_dir)

if __name__ == '__main__':
    if len(argv) < 2:
        print(GET_TODAY_GAMES_USAGE_STR)
    else:
        generate_today_game_svgs(argv[1])
