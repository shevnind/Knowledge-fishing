import uuid

from datetime import datetime
from sqlmodel import SQLModel, Field

class FishingSession(SQLModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    pond_id: str = Field()
    fish_id: str = Field()
