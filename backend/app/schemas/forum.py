import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ThreadCreate(BaseModel):
    title: str
    content: str


class ReplyCreate(BaseModel):
    content: str


class ReplyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    author_id: uuid.UUID
    content: str
    created_at: datetime


class ThreadRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    author_id: uuid.UUID
    title: str
    content: str
    created_at: datetime
