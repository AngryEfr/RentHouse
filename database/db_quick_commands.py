from sqlalchemy.exc import IntegrityError
from database.database import User, House, Booking, Payments, session
import datetime
import csv


def register_user(message, admin):
    username = message.from_user.username if message.from_user.username else None
    user = User(id=int(message.from_user.id), username=username, firstname=message.from_user.full_name, admin=admin)

    session.add(user)

    try:
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        return False


def get_active_house():
    house = session.query(House).filter(House.status == 'true')
    return house


def get_booking(message, name, id_house, date_begin, date_end):
    if type(date_end) is datetime.date:
        date_now = datetime.date.today()
        bookings = []
        date = date_end - date_begin
        payments = Payments(id_person=int(message.chat.id), id_house=id_house, comment=date.days, date_pay=date_now,
                            date_begin=date_begin)
        for i in range(date.days):
            booking = Booking(id_person=int(message.chat.id), name_person=name, id_house=id_house, date=date_begin)
            bookings.append(booking)
            date_begin += datetime.timedelta(days=1)
        payments.bookings = bookings
        session.add(payments)

    else:
        date_now = datetime.date.today()
        payments = Payments(id_person=int(message.chat.id), id_house=id_house, date_pay=date_now, date_begin=date_begin,
                            comment='1')
        booking = Booking(id_person=int(message.chat.id), name_person=name, id_house=id_house, date=date_begin)
        payments.bookings = [booking]
        session.add(payments)

    try:
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        return False


def check_date(date_check, house_id):
    dates = session.query(Booking).filter(Booking.date == date_check, Booking.id_house == house_id).first()
    if dates:
        return False
    else:
        return True


# def csv_save():
#     with open('mydump.csv', 'w', encoding='utf8', newline='') as outfile:
#         dt_now = datetime.date.today()
#         names = ["Ид", "Дом", "Ид_пол", "Имя", "Платеж", "Дата", "Телефон", "Подтверждение", "Въезд",
#                  "Выезд"]
#         outcsv = csv.writer(outfile, delimiter=",")
#         outcsv.writerow(names)
#         records = session.query(Booking).filter(Booking.date >= dt_now)
#         [outcsv.writerow([getattr(curr, column.name) for column in Booking.__mapper__.columns]) for curr in records]
#         return


def change_status_active(message, change: bool):
    user = session.query(User).filter(User.id == message.from_user.id).first()
    user.active = change

    session.add(user)

    try:
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        return False


def csv_save():
    with open('mydump.csv', 'w', encoding='utf8', newline='') as outfile:
        dt_now = datetime.date.today()
        names = ["Ид", "Дом", "Ид_пол", "Имя", "Платеж", "Дата", "Телефон", "Подтверждение", "Въезд",
                 "Выезд", 'Ид платежа', 'Дом', 'Имя', 'Дата брони', 'Дата заезда', 'Отправка увед.',
                 'Статус предоплаты', 'Подтверждение', 'Количество дней']
        outcsv = csv.writer(outfile, delimiter=",")
        outcsv.writerow(names)
        query = session.query(Booking, Payments).filter(Booking.date >= dt_now)
        query = query.join(Payments, Booking.id_payments == Payments.id)
        records = query.all()
        for record in records:
            outcsv.writerow([getattr(record[0], column.name) for column in Booking.__mapper__.columns] +
                            [getattr(record[1], column.name) for column in Payments.__mapper__.columns])
        return
