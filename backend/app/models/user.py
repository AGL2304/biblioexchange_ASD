import enum
import uuid

from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"


class AccountStatus(str, enum.Enum):
    actif = "actif"
    suspendu = "suspendu"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    nom = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)
    statut_compte = Column(Enum(AccountStatus), default=AccountStatus.actif, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    books = relationship("Book", back_populates="owner")
