import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.models.book import Book
from app.models.user import User
from app.schemas.book import BookRead

router = APIRouter()


@router.get("", response_model=list[BookRead])
def list_books(pending_only: bool = False, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    query = db.query(Book)
    if pending_only:
        query = query.filter(Book.valide_par_admin == False)  # noqa: E712
    return query.all()


@router.patch("/{book_id}/validate", response_model=BookRead)
def validate_book(book_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Livre introuvable")
    book.valide_par_admin = True
    db.commit()
    db.refresh(book)
    return book


@router.patch("/{book_id}/reject", response_model=BookRead)
def reject_book(book_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Livre introuvable")
    book.valide_par_admin = False
    db.commit()
    db.refresh(book)
    return book


@router.delete("/{book_id}", status_code=204)
def delete_book(book_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Livre introuvable")
    db.delete(book)
    db.commit()
