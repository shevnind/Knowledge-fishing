import uuid

from datetime import datetime
from sqlmodel import SQLModel, Field

class Fish(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    pond_id: str = Field()
    question: str = Field(max_length=1024)
    answer: str = Field(max_length=1024)
    interval: int = Field(default=0)
    repetitions: int = Field(default=0)
    ease_factor: float = Field(default=2.5)
    next_review_date: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})
    depth_level: int = Field(default=1)
    status: str = Field(default='ready')

