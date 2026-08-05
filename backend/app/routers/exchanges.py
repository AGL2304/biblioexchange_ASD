import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.book import Book, BookStatus
from app.models.exchange import Exchange, ExchangeStatus
from app.models.user import User
from app.schemas.exchange import ExchangeCreate, ExchangeRead

router = APIRouter()


def _get_participant_exchange(exchange_id: uuid.UUID, user: User, db: Session) -> Exchange:
    exchange = db.query(Exchange).filter(Exchange.id == exchange_id).first()
    if not exchange:
        raise HTTPException(status_code=404, detail="Échange introuvable")
    if user.id not in (exchange.user_a_id, exchange.user_b_id):
        raise HTTPException(status_code=403, detail="Vous ne participez pas à cet échange")
    return exchange


@router.post("", response_model=ExchangeRead, status_code=201)
def propose_exchange(payload: ExchangeCreate, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    offered = db.query(Book).filter(Book.id == payload.book_offered_id).first()
    requested = db.query(Book).filter(Book.id == payload.book_requested_id).first()

    if not offered or not requested:
        raise HTTPException(status_code=404, detail="Livre introuvable")
    if offered.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Vous ne possédez pas le livre proposé")
    if offered.statut != BookStatus.disponible or requested.statut != BookStatus.disponible:
        raise HTTPException(status_code=409, detail="L'un des deux livres n'est plus disponible")

    offered.statut = BookStatus.en_negociation
    requested.statut = BookStatus.en_negociation

    exchange = Exchange(
        book_offered_id=offered.id,
        book_requested_id=requested.id,
        user_a_id=user.id,
        user_b_id=requested.owner_id,
        statut=ExchangeStatus.propose,
    )
    db.add(exchange)
    db.commit()
    db.refresh(exchange)
    return exchange


@router.get("", response_model=list[ExchangeRead])
def list_my_exchanges(user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return db.query(Exchange).filter(
        (Exchange.user_a_id == user.id) | (Exchange.user_b_id == user.id)
    ).all()


@router.get("/{exchange_id}", response_model=ExchangeRead)
def get_exchange(exchange_id: uuid.UUID, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return _get_participant_exchange(exchange_id, user, db)


def _release_books(exchange: Exchange, db: Session):
    for book_id in (exchange.book_offered_id, exchange.book_requested_id):
        book = db.query(Book).filter(Book.id == book_id).first()
        if book:
            book.statut = BookStatus.disponible


@router.patch("/{exchange_id}/accept", response_model=ExchangeRead)
def accept_exchange(exchange_id: uuid.UUID, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    exchange = _get_participant_exchange(exchange_id, user, db)
    if user.id != exchange.user_b_id:
        raise HTTPException(status_code=403, detail="Seul le destinataire peut accepter la proposition")
    exchange.statut = ExchangeStatus.accepte
    db.commit()
    db.refresh(exchange)
    return exchange


@router.patch("/{exchange_id}/refuse", response_model=ExchangeRead)
def refuse_exchange(exchange_id: uuid.UUID, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    exchange = _get_participant_exchange(exchange_id, user, db)
    if user.id != exchange.user_b_id:
        raise HTTPException(status_code=403, detail="Seul le destinataire peut refuser la proposition")
    exchange.statut = ExchangeStatus.refuse
    _release_books(exchange, db)
    db.commit()
    db.refresh(exchange)
    return exchange


@router.patch("/{exchange_id}/cancel", response_model=ExchangeRead)
def cancel_exchange(exchange_id: uuid.UUID, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    exchange = _get_participant_exchange(exchange_id, user, db)
    exchange.statut = ExchangeStatus.annule
    _release_books(exchange, db)
    db.commit()
    db.refresh(exchange)
    return exchange


@router.patch("/{exchange_id}/complete", response_model=ExchangeRead)
def complete_exchange(exchange_id: uuid.UUID, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    exchange = _get_participant_exchange(exchange_id, user, db)
    offered = db.query(Book).filter(Book.id == exchange.book_offered_id).first()
    requested = db.query(Book).filter(Book.id == exchange.book_requested_id).first()

    # Transfert de propriété + retour à "disponible" pour une republication future
    offered.owner_id, requested.owner_id = requested.owner_id, offered.owner_id
    offered.statut = BookStatus.disponible
    requested.statut = BookStatus.disponible

    exchange.statut = ExchangeStatus.termine
    db.commit()
    db.refresh(exchange)
    return exchange
