import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict

from app.models.user import UserRole, AccountStatus


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    nom: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    nom: str
    role: UserRole
    created_at: datetime


class UserMe(UserPublic):
    email: EmailStr
    statut_compte: AccountStatus


class UserUpdate(BaseModel):
    nom: str | None = None


class CredentialsUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = None
