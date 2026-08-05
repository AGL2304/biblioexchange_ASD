import enum
import uuid

from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class BookStatus(str, enum.Enum):
    disponible = "disponible"
    indisponible = "indisponible"
    en_negociation = "en_negociation"


class Book(Base):
    __tablename__ = "books"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    titre = Column(String, nullable=False)
    auteur = Column(String, nullable=False)
    categorie = Column(String, nullable=True)
    etat = Column(String, nullable=True)
    statut = Column(Enum(BookStatus), default=BookStatus.disponible, nullable=False)
    valide_par_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="books")
