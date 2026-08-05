import enum
import uuid

from sqlalchemy import Column, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class ExchangeStatus(str, enum.Enum):
    propose = "propose"
    accepte = "accepte"
    refuse = "refuse"
    annule = "annule"
    termine = "termine"


class Exchange(Base):
    __tablename__ = "exchanges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_offered_id = Column(UUID(as_uuid=True), ForeignKey("books.id"), nullable=False)
    book_requested_id = Column(UUID(as_uuid=True), ForeignKey("books.id"), nullable=False)
    user_a_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user_b_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    statut = Column(Enum(ExchangeStatus), default=ExchangeStatus.propose, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
