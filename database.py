import os

from sqlmodel import create_engine, SQLModel
from typing import TYPE_CHECKING


db_path = os.getenv('DATABASE_PATH', '/data/database.db')
sqlite_url = f'sqlite:///{db_path}'
engine = create_engine(sqlite_url, echo=True)

def create_table():
    SQLModel.metadata.create_all(engine)
