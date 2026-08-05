import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.models.book import Book, BookStatus
from app.models.exchange import Exchange, ExchangeStatus
from app.models.user import User
from app.schemas.exchange import ExchangeRead

router = APIRouter()


@router.get("", response_model=list[ExchangeRead])
def list_exchanges(statut: ExchangeStatus | None = None, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    query = db.query(Exchange)
    if statut:
        query = query.filter(Exchange.statut == statut)
    return query.all()


@router.get("/{exchange_id}", response_model=ExchangeRead)
def get_exchange(exchange_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    exchange = db.query(Exchange).filter(Exchange.id == exchange_id).first()
    if not exchange:
        raise HTTPException(status_code=404, detail="Échange introuvable")
    return exchange


@router.patch("/{exchange_id}/force-cancel", response_model=ExchangeRead)
def force_cancel(exchange_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    exchange = db.query(Exchange).filter(Exchange.id == exchange_id).first()
    if not exchange:
        raise HTTPException(status_code=404, detail="Échange introuvable")
    exchange.statut = ExchangeStatus.annule
    for book_id in (exchange.book_offered_id, exchange.book_requested_id):
        book = db.query(Book).filter(Book.id == book_id).first()
        if book:
            book.statut = BookStatus.disponible
    db.commit()
    db.refresh(exchange)
    return exchange
