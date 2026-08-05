import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.report import ReportTargetType, ReportStatus


class ReportCreate(BaseModel):
    cible_type: ReportTargetType
    cible_id: uuid.UUID
    motif: str


class ReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    signale_par_id: uuid.UUID
    cible_type: ReportTargetType
    cible_id: uuid.UUID
    motif: str
    statut: ReportStatus
    created_at: datetime
