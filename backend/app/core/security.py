"""Hash de mot de passe, émission/validation JWT, dépendances RBAC."""
import logging
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User, UserRole, AccountStatus

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Logger dédié à l'audit des accès admin (alimente l'alerte de supervision
# "accès admin non autorisé" définie dans monitoring/prometheus/alerts.yml)
audit_logger = logging.getLogger("biblioexchange.audit")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expires_minutes)
    payload = {"sub": subject, "exp": expire, "iat": datetime.now(timezone.utc)}
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identifiants invalides",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        raw_id: str | None = payload.get("sub")
        if raw_id is None:
            raise credentials_exception
        user_id = uuid.UUID(raw_id)
    except (JWTError, ValueError):
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(user: User = Depends(get_current_user)) -> User:
    if user.statut_compte == AccountStatus.suspendu:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Compte suspendu")
    return user


def require_admin(user: User = Depends(get_current_active_user)) -> User:
    if user.role != UserRole.admin:
        audit_logger.warning(
            "unauthorized_admin_access", extra={"user_id": str(user.id), "email": user.email}
        )
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès réservé aux administrateurs")
    return user
