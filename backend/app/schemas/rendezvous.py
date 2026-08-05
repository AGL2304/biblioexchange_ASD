import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.rendezvous import RendezvousStatus


class RendezvousCreate(BaseModel):
    lieu: str
    date_heure: datetime
    duree_minutes: int


class RendezvousRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    exchange_id: uuid.UUID
    lieu: str
    date_heure: datetime
    duree_minutes: int
    statut: RendezvousStatus
