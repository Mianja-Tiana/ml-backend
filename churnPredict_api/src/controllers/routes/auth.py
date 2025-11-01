# app/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import timedelta

from models.model import User
from schemas.schema import UserCreate, Token
from auth.security import (
    verify_password,
    get_password_hash,
    create_access_token,
)
from db.database import get_session

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=dict)
def register(user_data: UserCreate, session: Session = Depends(get_session)):
    user_exists = session.exec(select(User).where(User.username == user_data.username)).first()
    if user_exists:
        raise HTTPException(status_code=400, detail="Username already taken")

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return {"message": "User registered successfully"}


from fastapi.security import OAuth2PasswordRequestForm

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    # form_data is now an instance of OAuth2PasswordRequestForm
    user = session.exec(select(User).where(User.username == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=timedelta(minutes=30)
    )
    return {"access_token": access_token, "token_type": "bearer"}



# @router.post("/login", response_model=Token)
# def login(form_data: Depends = Depends(), session: Session = Depends(get_session)):
#     from fastapi.security import OAuth2PasswordRequestForm
#     form_data: OAuth2PasswordRequestForm = form_data

#     user = session.exec(select(User).where(User.username == form_data.username)).first()
#     if not user or not verify_password(form_data.password, user.hashed_password):
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

#     access_token_expires = timedelta(minutes=30)
#     access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

#     return {"access_token": access_token, "token_type": "bearer"}
