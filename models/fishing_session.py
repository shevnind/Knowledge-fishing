import uuid

from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from models.user import User

class FishingSession(SQLModel, table=True):
    __tablename__ = 'fishing_session'
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    pond_id: str = Field()
    fish_id: str = Field()

    user: Optional["User"] = Relationship(back_populates='fishing_session')
