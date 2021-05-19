import baseball
import datetime


def get_todays_games():
    start = datetime.datetime(2019, 1, 1)
    end = datetime.datetime(2021, 12, 31)
    interval = datetime.timedelta(days=1)
    this_date = start

    while this_date <= end:
        print(this_date)
        baseball.write_games_for_date(this_date, '/var/www/html/new', True, True, True)
        this_date = this_date + interval

if __name__ == '__main__':
    get_todays_games()

