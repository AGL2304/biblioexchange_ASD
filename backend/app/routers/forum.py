import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.forum import ForumThread, ForumReply
from app.models.user import User
from app.schemas.forum import ThreadCreate, ThreadRead, ReplyCreate, ReplyRead

router = APIRouter()


@router.get("/threads", response_model=list[ThreadRead])
def list_threads(db: Session = Depends(get_db)):
    return db.query(ForumThread).order_by(ForumThread.created_at.desc()).all()


@router.post("/threads", response_model=ThreadRead, status_code=201)
def create_thread(payload: ThreadCreate, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    thread = ForumThread(author_id=user.id, **payload.model_dump())
    db.add(thread)
    db.commit()
    db.refresh(thread)
    return thread


@router.get("/threads/{thread_id}", response_model=ThreadRead)
def get_thread(thread_id: uuid.UUID, db: Session = Depends(get_db)):
    thread = db.query(ForumThread).filter(ForumThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Sujet introuvable")
    return thread


@router.get("/threads/{thread_id}/replies", response_model=list[ReplyRead])
def list_replies(thread_id: uuid.UUID, db: Session = Depends(get_db)):
    return db.query(ForumReply).filter(ForumReply.thread_id == thread_id).order_by(ForumReply.created_at).all()


@router.post("/threads/{thread_id}/replies", response_model=ReplyRead, status_code=201)
def reply_to_thread(thread_id: uuid.UUID, payload: ReplyCreate, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if not db.query(ForumThread).filter(ForumThread.id == thread_id).first():
        raise HTTPException(status_code=404, detail="Sujet introuvable")
    reply = ForumReply(thread_id=thread_id, author_id=user.id, **payload.model_dump())
    db.add(reply)
    db.commit()
    db.refresh(reply)
    return reply
