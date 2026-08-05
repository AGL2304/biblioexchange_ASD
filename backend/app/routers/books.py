import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.book import Book, BookStatus
from app.models.user import User
from app.schemas.book import BookCreate, BookUpdate, BookRead, BookStatusUpdate

router = APIRouter()


@router.get("", response_model=list[BookRead])
def list_books(q: str | None = None, categorie: str | None = None, db: Session = Depends(get_db)):
    """Catalogue public : uniquement les livres disponibles et validés par un admin."""
    query = db.query(Book).filter(Book.statut == BookStatus.disponible, Book.valide_par_admin == True)  # noqa: E712
    if q:
        like = f"%{q}%"
        query = query.filter((Book.titre.ilike(like)) | (Book.auteur.ilike(like)))
    if categorie:
        query = query.filter(Book.categorie == categorie)
    return query.all()


@router.get("/mine", response_model=list[BookRead])
def list_my_books(user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return db.query(Book).filter(Book.owner_id == user.id).all()


@router.get("/{book_id}", response_model=BookRead)
def get_book(book_id: uuid.UUID, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Livre introuvable")
    return book


@router.post("", response_model=BookRead, status_code=201)
def create_book(payload: BookCreate, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    book = Book(owner_id=user.id, valide_par_admin=False, **payload.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def _get_owned_book(book_id: uuid.UUID, user: User, db: Session) -> Book:
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Livre introuvable")
    if book.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Vous n'êtes pas propriétaire de ce livre")
    return book


@router.patch("/{book_id}", response_model=BookRead)
def update_book(book_id: uuid.UUID, payload: BookUpdate, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    book = _get_owned_book(book_id, user, db)
    if book.statut == BookStatus.en_negociation:
        raise HTTPException(status_code=409, detail="Livre en négociation : modification impossible")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(book, field, value)
    db.commit()
    db.refresh(book)
    return book


@router.delete("/{book_id}", status_code=204)
def delete_book(book_id: uuid.UUID, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    book = _get_owned_book(book_id, user, db)
    if book.statut == BookStatus.en_negociation:
        raise HTTPException(status_code=409, detail="Livre en négociation : suppression impossible")
    db.delete(book)
    db.commit()


@router.patch("/{book_id}/status", response_model=BookRead)
def update_book_status(book_id: uuid.UUID, payload: BookStatusUpdate, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    book = _get_owned_book(book_id, user, db)
    if book.statut == BookStatus.en_negociation:
        raise HTTPException(status_code=409, detail="Livre en négociation : statut verrouillé")
    book.statut = payload.statut
    db.commit()
    db.refresh(book)
    return book
