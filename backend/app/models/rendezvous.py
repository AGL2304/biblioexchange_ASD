import enum
import uuid

from sqlalchemy import Column, String, DateTime, Integer, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class RendezvousStatus(str, enum.Enum):
    prevu = "prevu"
    confirme = "confirme"
    passe = "passe"
    annule = "annule"


class Rendezvous(Base):
    __tablename__ = "rendezvous"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exchange_id = Column(UUID(as_uuid=True), ForeignKey("exchanges.id"), nullable=False, unique=True)
    lieu = Column(String, nullable=False)
    date_heure = Column(DateTime(timezone=True), nullable=False)
    duree_minutes = Column(Integer, nullable=False)
    statut = Column(Enum(RendezvousStatus), default=RendezvousStatus.prevu, nullable=False)
