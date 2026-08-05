import enum
import uuid

from sqlalchemy import Column, String, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class ReportTargetType(str, enum.Enum):
    user = "user"
    book = "book"


class ReportStatus(str, enum.Enum):
    ouvert = "ouvert"
    traite = "traite"


class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    signale_par_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    cible_type = Column(Enum(ReportTargetType), nullable=False)
    cible_id = Column(UUID(as_uuid=True), nullable=False)
    motif = Column(String, nullable=False)
    statut = Column(Enum(ReportStatus), default=ReportStatus.ouvert, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
