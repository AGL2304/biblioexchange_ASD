from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.report import Report
from app.models.user import User
from app.schemas.report import ReportCreate, ReportRead

router = APIRouter()


@router.post("", response_model=ReportRead, status_code=201)
def create_report(payload: ReportCreate, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    report = Report(signale_par_id=user.id, **payload.model_dump())
    db.add(report)
    db.commit()
    db.refresh(report)
    return report
