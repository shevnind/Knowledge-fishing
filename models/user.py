import uuid

from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    cur_fishing_session_id: str = Field(default="-1")

