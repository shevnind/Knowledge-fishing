import uuid

from datetime import datetime
from sqlmodel import SQLModel, Field


class Pond(SQLModel):
    id: str = Field(default_factory=lambda : str(uuid.uuid64()), primary_key=True)
    user_id: str = Field()
    name: str = Field(max_length=128)
    description: str = Field(max_length=1024)
    topic: str = Field(max_length=128)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate" : datetime.now})

