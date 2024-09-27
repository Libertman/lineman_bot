from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker



DATABASE_URL = "sqlite:///users.db"
engine = create_engine(DATABASE_URL)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    deadlines = Column(list, nullable=True)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

def add_user(telegram_id, username=None, first_name=None, last_name=None, deadlines=None):
    user = User(telegram_id=telegram_id, username=username, first_name=first_name, last_name=last_name, deadlines=deadlines)
    session.add(user)
    session.commit()

def get_user(telegram_id):
    return session.query(User).filter_by(telegram_id=telegram_id).first()

def update_user(telegram_id, deadlines):
    user = get_user(telegram_id)
    if user:
        user.deadlines = deadlines
        session.commit()

def delete_user(telegram_id):
    user = get_user(telegram_id)
    if user:
        session.delete(user)
        session.commit()