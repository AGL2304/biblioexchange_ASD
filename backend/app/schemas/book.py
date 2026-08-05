import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.book import BookStatus


class BookCreate(BaseModel):
    titre: str
    auteur: str
    categorie: str | None = None
    etat: str | None = None


class BookUpdate(BaseModel):
    titre: str | None = None
    auteur: str | None = None
    categorie: str | None = None
    etat: str | None = None


class BookStatusUpdate(BaseModel):
    statut: BookStatus


class BookRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    owner_id: uuid.UUID
    titre: str
    auteur: str
    categorie: str | None
    etat: str | None
    statut: BookStatus
    valide_par_admin: bool
    created_at: datetime
