import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationRead

router = APIRouter()


@router.get("", response_model=list[NotificationRead])
def list_notifications(user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return db.query(Notification).filter(Notification.user_id == user.id).order_by(Notification.created_at.desc()).all()


@router.patch("/{notif_id}/read", response_model=NotificationRead)
def mark_read(notif_id: uuid.UUID, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    notif = db.query(Notification).filter(Notification.id == notif_id, Notification.user_id == user.id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification introuvable")
    notif.read = True
    db.commit()
    db.refresh(notif)
    return notif
