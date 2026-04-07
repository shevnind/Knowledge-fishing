# import os

# from sqlmodel import create_engine, SQLModel
# from typing import TYPE_CHECKING


# db_path = os.getenv('DATABASE_PATH')
# sqlite_url = f'sqlite:///{db_path}'
# engine = create_engine(sqlite_url, echo=False)

# def create_table():
#     SQLModel.metadata.create_all(engine)


import os
from sqlmodel import create_engine, SQLModel

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "appdb")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "secret")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, echo=False)

def create_table():
    SQLModel.metadata.create_all(engine)
