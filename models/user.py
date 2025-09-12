import uuid

from typing import List, TYPE_CHECKING, Optional
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from models.pond import Pond

if TYPE_CHECKING:
    from models.fishing_session import FishingSession


class User(SQLModel, table=True):
    #__tablename__ = "users"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    cur_fishing_session_id: str = Field(default="-1", foreign_key='fishing_session.id')

    ponds: List["Pond"] = Relationship(back_populates='user')
    fishing_session: Optional["FishingSession"] = Relationship(back_populates='user')
