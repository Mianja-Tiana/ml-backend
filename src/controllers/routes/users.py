from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.models.users import UserCreate, UserLogin, UserResponse, Token
from datetime import timedelta, date
from src.schemas.users import User as users_schema
from src.utils.response_wrapper import api_response
from src.controllers.middleware.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

router = APIRouter()

@router.post("/register")
def register(user_data: UserCreate, db: Session = Depends(get_db)):    
   
    db_user = db.query(users_schema).filter(users_schema.phone == user_data.phone).first()
    if db_user:
        raise HTTPException(status_code=400, detail="user already exists")
    
    hashed_password = get_password_hash(user_data.password)

    # Auto-generate created_at, updated_at, is_active if None 
    now = date.today()  
    user_data_dump = user_data.model_dump(exclude_unset=True)  # (None)
    
    
    if 'created_at' not in user_data_dump or user_data_dump['created_at'] is None:
        user_data_dump['created_at'] = now
    if 'updated_at' not in user_data_dump or user_data_dump['updated_at'] is None:
        user_data_dump['updated_at'] = now
    if 'is_active' not in user_data_dump or user_data_dump['is_active'] is None:
        user_data_dump['is_active'] = True  # New users actifs by défaut

    new_user = users_schema(**user_data_dump)
    new_user.password = hashed_password
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    user_response = UserResponse(
        id=new_user.id,
        phone=new_user.phone,
        full_name=new_user.full_name,
        email=new_user.email,
        team=new_user.team,
        address=new_user.address,
        role=new_user.role,
        created_at=new_user.created_at,
        updated_at=new_user.updated_at,
        is_active=new_user.is_active,
    )
    
    return api_response(data=user_response, message="user registered successfully")


@router.post("/login")
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    db_user = (
        db.query(users_schema)
        .filter((users_schema.phone == login_data.username) | (users_schema.email == login_data.username))
        .first()
    )

    if not db_user or not verify_password(login_data.password, db_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": db_user.phone}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    token = Token(access_token=access_token, token_type="bearer")
    return api_response(data=token, message="login successful")