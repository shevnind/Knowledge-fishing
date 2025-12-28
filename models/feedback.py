import uuid
import json

from typing import TYPE_CHECKING
from datetime import datetime, timedelta, timezone
from sqlmodel import SQLModel, Field, ForeignKey, Relationship

if TYPE_CHECKING:
    from models.user import User

def get_current_datetime():
    return datetime.now()


class FeedBack(SQLModel, table=True):
    id: str = Field(default_factory=lambda : str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key='user.id')
    type: str = Field()
    text: str = Field()
    created_at: datetime = Field(default_factory=get_current_datetime)
    solved_at: datetime = Field(default=datetime(1970, 1, 1))
    solved: bool = Field(default=False)
    solution: str = Field(default="")
