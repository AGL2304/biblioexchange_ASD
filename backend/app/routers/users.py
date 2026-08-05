import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user, hash_password
from app.models.user import User
from app.models.exchange import Exchange
from app.schemas.user import UserMe, UserPublic, UserUpdate, CredentialsUpdate
from app.schemas.exchange import ExchangeRead

router = APIRouter()


@router.get("/me", response_model=UserMe)
def read_me(user: User = Depends(get_current_active_user)):
    return user


@router.patch("/me", response_model=UserMe)
def update_me(payload: UserUpdate, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if payload.nom is not None:
        user.nom = payload.nom
    db.commit()
    db.refresh(user)
    return user


@router.patch("/me/credentials", response_model=UserMe)
def update_credentials(payload: CredentialsUpdate, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if payload.email is not None:
        user.email = payload.email
    if payload.password is not None:
        user.password_hash = hash_password(payload.password)
    db.commit()
    db.refresh(user)
    return user


@router.get("/me/exchanges", response_model=list[ExchangeRead])
def my_exchanges(user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return db.query(Exchange).filter(
        (Exchange.user_a_id == user.id) | (Exchange.user_b_id == user.id)
    ).all()


@router.get("/{user_id}", response_model=UserPublic)
def read_public_profile(user_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_active_user)):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return target
