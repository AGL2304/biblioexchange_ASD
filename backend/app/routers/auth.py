from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, get_current_user
from app.models.user import User
from app.schemas.auth import Token
from app.schemas.user import UserRegister, UserMe

router = APIRouter()


@router.post("/register", response_model=UserMe, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Un compte existe déjà avec cet email")
    user = User(email=payload.email, password_hash=hash_password(payload.password), nom=payload.nom)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou mot de passe incorrect")
    return Token(access_token=create_access_token(str(user.id)))


@router.post("/refresh", response_model=Token)
def refresh(user: User = Depends(get_current_user)):
    return Token(access_token=create_access_token(str(user.id)))
