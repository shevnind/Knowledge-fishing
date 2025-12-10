import uuid
import bcrypt

from typing import List, TYPE_CHECKING, Optional
from sqlmodel import SQLModel, Field, Relationship
from passlib.context import CryptContext

if TYPE_CHECKING:
    from models.pond import Pond

if TYPE_CHECKING:
    from models.fishing_session import FishingSession


hash_context = CryptContext(
    schemes=["bcrypt"],
    deprecated='auto',
    bcrypt__rounds=10
)


class User(SQLModel, table=True):
    #__tablename__ = "users"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    login: str = Field(default="")
    hashed_password: str = Field(default="")
    cur_fishing_session_id: str = Field(default="-1", foreign_key='fishing_session.id')
    admin: bool = Field(default=False)

    ponds: List["Pond"] = Relationship(back_populates='user')
    fishing_session: Optional["FishingSession"] = Relationship(back_populates='user')

    @classmethod
    def hash_password(cls, password: str):
        return hash_context.hash(password)

    def check_password(self, password: str):
        return hash_context.verify(password, self.hashed_password)

