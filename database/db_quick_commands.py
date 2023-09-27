from sqlalchemy.exc import IntegrityError
from database.database import User, House, Booking, Payments, session
import datetime


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
        date = date_end - date_begin
        for i in range(date.days):
            booking = Booking(id_person=int(message.chat.id), name_person=name, id_house=id_house, date=date_begin)
            session.add(booking)
            date_begin += datetime.timedelta(days=1)
    else:
        booking = Booking(id_person=int(message.chat.id), name_person=name, id_house=id_house, date=date_begin)
        session.add(booking)

    try:
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        return False
