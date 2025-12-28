import uuid

from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from models.pond import Pond


def get_current_datetime():
    return datetime.now()


class Fish(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    pond_id: str = Field(foreign_key='pond.id')
    question: str = Field(max_length=1024)
    answer: str = Field(max_length=1024)
    repetitions: int = Field(default=0)
    next_review_date: datetime = Field(default_factory=get_current_datetime)
    created_at: datetime = Field(default_factory=get_current_datetime)
    updated_at: datetime = Field(default_factory=get_current_datetime)
    depth_level: int = Field(default=0)
    ready: bool = Field(default=False)

    pond: Optional["Pond"] = Relationship(back_populates='fishes')
