import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.models.report import Report, ReportStatus
from app.models.user import User
from app.schemas.report import ReportRead

router = APIRouter()


@router.get("", response_model=list[ReportRead])
def list_reports(statut: ReportStatus | None = None, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    query = db.query(Report)
    if statut:
        query = query.filter(Report.statut == statut)
    return query.all()


@router.patch("/{report_id}/resolve", response_model=ReportRead)
def resolve_report(report_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Signalement introuvable")
    report.statut = ReportStatus.traite
    db.commit()
    db.refresh(report)
    return report
