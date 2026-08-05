import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.exchange import Exchange
from app.models.rendezvous import Rendezvous, RendezvousStatus
from app.models.user import User
from app.schemas.rendezvous import RendezvousCreate, RendezvousRead

router = APIRouter()


def _assert_participant(exchange: Exchange, user: User):
    if user.id not in (exchange.user_a_id, exchange.user_b_id):
        raise HTTPException(status_code=403, detail="Vous ne participez pas à cet échange")


@router.post("/exchanges/{exchange_id}/rendezvous", response_model=RendezvousRead, status_code=201)
def propose_rendezvous(exchange_id: uuid.UUID, payload: RendezvousCreate, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    exchange = db.query(Exchange).filter(Exchange.id == exchange_id).first()
    if not exchange:
        raise HTTPException(status_code=404, detail="Échange introuvable")
    _assert_participant(exchange, user)

    if db.query(Rendezvous).filter(Rendezvous.exchange_id == exchange_id).first():
        raise HTTPException(status_code=409, detail="Un rendez-vous existe déjà pour cet échange")

    rdv = Rendezvous(exchange_id=exchange_id, **payload.model_dump())
    db.add(rdv)
    db.commit()
    db.refresh(rdv)
    return rdv


@router.get("/exchanges/{exchange_id}/rendezvous", response_model=RendezvousRead)
def get_rendezvous(exchange_id: uuid.UUID, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    exchange = db.query(Exchange).filter(Exchange.id == exchange_id).first()
    if not exchange:
        raise HTTPException(status_code=404, detail="Échange introuvable")
    _assert_participant(exchange, user)
    rdv = db.query(Rendezvous).filter(Rendezvous.exchange_id == exchange_id).first()
    if not rdv:
        raise HTTPException(status_code=404, detail="Aucun rendez-vous pour cet échange")
    return rdv


def _get_owned_rendezvous(rdv_id: uuid.UUID, user: User, db: Session) -> Rendezvous:
    rdv = db.query(Rendezvous).filter(Rendezvous.id == rdv_id).first()
    if not rdv:
        raise HTTPException(status_code=404, detail="Rendez-vous introuvable")
    exchange = db.query(Exchange).filter(Exchange.id == rdv.exchange_id).first()
    _assert_participant(exchange, user)
    return rdv


@router.patch("/rendezvous/{rdv_id}/confirm", response_model=RendezvousRead)
def confirm_rendezvous(rdv_id: uuid.UUID, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    rdv = _get_owned_rendezvous(rdv_id, user, db)
    rdv.statut = RendezvousStatus.confirme
    db.commit()
    db.refresh(rdv)
    return rdv


@router.patch("/rendezvous/{rdv_id}/cancel", response_model=RendezvousRead)
def cancel_rendezvous(rdv_id: uuid.UUID, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    rdv = _get_owned_rendezvous(rdv_id, user, db)
    rdv.statut = RendezvousStatus.annule
    db.commit()
    db.refresh(rdv)
    return rdv
