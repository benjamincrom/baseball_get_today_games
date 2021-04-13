import baseball

from ddtrace import tracer

@tracer.wrap(service='get-todays-games')
def get_todays_games():
    baseball.generate_today_game_svgs("/var/www/html", True, True, True)

if __name__ == '__main__':
    get_todays_games()

