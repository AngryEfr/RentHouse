from config_data.config import Config, load_config
from sqlalchemy import create_engine, Column, String, BigInteger, Boolean, Integer, Date, ForeignKey
from sqlalchemy.orm import scoped_session, declarative_base, sessionmaker, relationship


config: Config = load_config('.env')

engine = create_engine(f"postgresql+psycopg2://postgres:{config.db.db_password}@{config.db.db_host}/"
                       f"{config.db.database}")
session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()
Base.query = session.query_property()


class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True)       # Ид
    username = Column(String)                       # Логин
    firstname = Column(String)                      # Имя
    active = Column(Boolean, default=True)          # Активный пользователь
    admin = Column(Boolean, default=False)          # Админ


class House(Base):
    __tablename__ = 'house'

    id = Column(Integer, primary_key=True)          # Ид
    name = Column(String)                           # Название дома
    link = Column(String)                           # Ссылка на телеграф
    status = Column(Boolean, default=True)          # Активный дом


class Booking(Base):
    __tablename__ = 'booking'

    id = Column(BigInteger, primary_key=True)       # Ид брони
    id_house = Column(Integer)                      # Ид дома
    id_person = Column(BigInteger)                  # Ид пользователя
    name_person = Column(String)                    # Имя
    id_payments = Column(Integer, ForeignKey("payments.id"))                   # Ид платежа
    date = Column(Date)                             # Дата
    status_confirm = Column(Boolean, default=None)  # Статус брони
    check_in = Column(Boolean, default=None)        # Статус заезда
    end = Column(Boolean, default=False)            # Конец

    payments = relationship("Payments", back_populates='bookings')


class Payments(Base):
    __tablename__ = 'payments'

    id = Column(BigInteger, primary_key=True)       # Ид платежа
    id_house = Column(Integer)                      # Ид дома
    id_person = Column(BigInteger)                  # Ид пользователя
    sending = Column(Boolean)                       # Отправка данных для платежа (админом)
    status = Column(Boolean, default=False)         # Статус платежа (меняется пользователем для проверки)
    confirm = Column(Boolean)                       # Подтверждение платежа (админом)
    bookings = relationship("Booking", back_populates='payments')
    comment = Column(String)                        # Комментарий (количество дней)


Base.metadata.create_all(bind=engine)
