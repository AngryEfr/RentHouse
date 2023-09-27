
import datetime


def change_the_date(message):
    if 8 <= len(message) <= 10:
        date = message.split('.')
        date_begin = datetime.date(int(date[2]), int(date[1]), int(date[0]))
        date_end = "Выезд на следующий день"
        return date_begin, date_end
    else:
        dates = message.split(' - ')
        date1 = dates[0].split('.')
        date2 = dates[1].split('.')
        date_begin = datetime.date(int(date1[2]), int(date1[1]), int(date1[0]))
        date_end = datetime.date(int(date2[2]), int(date2[1]), int(date2[0]))
        return date_begin, date_end

