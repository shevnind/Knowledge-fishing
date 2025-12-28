import uuid
import json

from typing import Optional, TYPE_CHECKING, List
from datetime import datetime, timedelta, timezone
from enum import Enum
from sqlmodel import SQLModel, Field, ForeignKey, Relationship

if TYPE_CHECKING:
    from models.user import User

if TYPE_CHECKING:
    from models.fish import Fish


class PondType(Enum):
    OWN = 0
    COPIED = 1
    COPIED_WITH_UPDATE = 2


default_pond_intervals = [timedelta(hours=1), timedelta(days=1), timedelta(days=7), timedelta(days=30)]


def get_current_utc_datetime():
    return datetime.now(timezone.utc)


class Pond(SQLModel, table=True):
    id: str = Field(default_factory=lambda : str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key='user.id')
    name: str = Field(max_length=128)
    description: str = Field(max_length=1024)
    topic: str = Field(max_length=128)
    created_at: datetime = Field(default_factory=get_current_utc_datetime)
    updated_at: datetime = Field(default_factory=get_current_utc_datetime, sa_column_kwargs={"onupdate" : get_current_utc_datetime})
    intervals: str = Field(default_factory=lambda: json.dumps([td.total_seconds() for td in default_pond_intervals]))
    cnt_fishes: int = Field(default=0)
    cnt_ready_fishes: int = Field(default=0)
    public: bool = Field(default=False)
    pond_type: int = Field(default=0)
    cnt_copied: int = Field(default=0)
    copied_from_id: str = Field(nullable=True)
    last_update_from_original: datetime = Field(default_factory=get_current_utc_datetime)

    user: Optional["User"] = Relationship(back_populates='ponds')
    fishes: List["Fish"] = Relationship(back_populates='pond')

    def get_intervals(self) -> List[timedelta]:
        seconds_list = json.loads(self.intervals)
        return [timedelta(seconds=seconds) for seconds in seconds_list]
    
    def set_intervals(self, value: List[timedelta]):    
        self.intervals = json.dumps([td.total_seconds() for td in value])

