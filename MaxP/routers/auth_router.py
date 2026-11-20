from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import auth
import models
import schemas
from database import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Реєстрація",
)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    email = user_data.email.lower()

    if db.scalar(select(models.User.id).where(func.lower(models.User.username) == user_data.username.lower())):
        raise HTTPException(status.HTTP_409_CONFLICT, "Користувач із таким ім'ям вже існує")
    if db.scalar(select(models.User.id).where(func.lower(models.User.email) == email)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Цей email вже зареєстровано")

    new_user = models.User(
        username=user_data.username,
        email=email,
        hashed_password=auth.get_password_hash(user_data.password),
    )
    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Такий користувач вже існує")
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=schemas.Token, summary="Вхід (за ім'ям або email)")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    ident = form_data.username.strip()
    user = db.scalar(
        select(models.User).where(
            or_(models.User.username == ident, func.lower(models.User.email) == ident.lower())
        )
    )
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірне ім'я користувача або пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": auth.create_access_token(user.id), "token_type": "bearer"}


@router.get("/me", response_model=schemas.UserResponse, summary="Мій профіль")
def me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user
