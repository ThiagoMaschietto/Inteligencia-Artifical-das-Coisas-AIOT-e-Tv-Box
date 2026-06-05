from sqlmodel import create_engine, Session
from dotenv import load_dotenv
from os import getenv

load_dotenv()
sqlite_url = getenv('DATABASE_URL')

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo =True, connect_args=connect_args)

def get_session():
    with Session(engine) as session:
        yield session