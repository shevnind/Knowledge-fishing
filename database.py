import os

from sqlmodel import create_engine, SQLModel
from typing import TYPE_CHECKING


db_path = os.getenv('DATABASE_PATH')
sqlite_url = f'sqlite:///{db_path}'
engine = create_engine(sqlite_url, echo=False)

def create_table():
    SQLModel.metadata.create_all(engine)
