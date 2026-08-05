from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.models.book import Book
from app.models.exchange import Exchange, ExchangeStatus
from app.models.report import Report, ReportStatus
from app.models.user import User

router = APIRouter()


@router.get("/exchanges")
def exchange_stats(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    since = datetime.now(timezone.utc) - timedelta(days=1)
    return {
        "crees_24h": db.query(Exchange).filter(Exchange.created_at >= since).count(),
        "termines": db.query(Exchange).filter(Exchange.statut == ExchangeStatus.termine).count(),
        "annules": db.query(Exchange).filter(Exchange.statut == ExchangeStatus.annule).count(),
        "en_cours": db.query(Exchange).filter(
            Exchange.statut.in_([ExchangeStatus.propose, ExchangeStatus.accepte])
        ).count(),
    }


@router.get("/moderation")
def moderation_stats(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    total_books = db.query(Book).count()
    pending = db.query(Book).filter(Book.valide_par_admin == False).count()  # noqa: E712
    return {
        "livres_total": total_books,
        "livres_en_attente": pending,
        "signalements_ouverts": db.query(Report).filter(Report.statut == ReportStatus.ouvert).count(),
    }
