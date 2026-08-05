import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.models.user import User, AccountStatus
from app.schemas.user import UserMe

router = APIRouter()


@router.get("", response_model=list[UserMe])
def list_users(statut: AccountStatus | None = None, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    query = db.query(User)
    if statut:
        query = query.filter(User.statut_compte == statut)
    return query.all()


@router.get("/{user_id}", response_model=UserMe)
def get_user(user_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return user


@router.patch("/{user_id}/suspend", response_model=UserMe)
def suspend_user(user_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    user.statut_compte = AccountStatus.suspendu
    db.commit()
    db.refresh(user)
    return user


@router.patch("/{user_id}/reactivate", response_model=UserMe)
def reactivate_user(user_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    user.statut_compte = AccountStatus.actif
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    db.delete(user)
    db.commit()
