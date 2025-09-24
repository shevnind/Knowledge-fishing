from sqlmodel import create_engine, SQLModel
from typing import TYPE_CHECKING


sqlite_url = 'sqlite:///database.db'
engine = create_engine(sqlite_url, echo=True)

def create_table():
    SQLModel.metadata.create_all(engine)
