import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.exchange import ExchangeStatus


class ExchangeCreate(BaseModel):
    book_offered_id: uuid.UUID
    book_requested_id: uuid.UUID


class ExchangeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    book_offered_id: uuid.UUID
    book_requested_id: uuid.UUID
    user_a_id: uuid.UUID
    user_b_id: uuid.UUID
    statut: ExchangeStatus
    created_at: datetime
