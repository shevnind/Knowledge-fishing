import uuid

from typing import Optional, TYPE_CHECKING, List
from datetime import datetime, timedelta
from sqlmodel import SQLModel, Field, ForeignKey, Relationship

if TYPE_CHECKING:
    from models.user import User

if TYPE_CHECKING:
    from models.fish import Fish


default_pond_intervals = [timedelta(hours=1), timedelta(days=1), timedelta(days=7), timedelta(days=30)]


class Pond(SQLModel, table=True):
    id: str = Field(default_factory=lambda : str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key='user.id')
    name: str = Field(max_length=128)
    description: str = Field(max_length=1024)
    topic: str = Field(max_length=128)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate" : datetime.now})
    interval: List[timedelta] = Field(default=default_pond_intervals)

    user: Optional["User"] = Relationship(back_populates='ponds')
    fishes: List["Fish"] = Relationship(back_populates='pond')

