import os
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jwt.exceptions import InvalidTokenError
from fastapi.security import OAuth2PasswordBearer
from pathlib import Path
from pwdlib import PasswordHash
from sqlmodel import Session, select
#from dotenv import load_dotenv

from models.model import User
from db.database import get_session


SECRET_KEY = ""
ALGORITHM = ""
ACCESS_TOKEN_EXPIRE_MINUTES = 0


secret_path = Path("/run/secrets/secrete_key")
if secret_path.exists():
    SECRET_KEY = secret_path.read_text().strip()
    ALGORITHM = Path("/run/secrets/algorithm").read_text().strip() or "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = Path("/run/secrets/access_token_expire_minutes").read_text().strip()
    if not ACCESS_TOKEN_EXPIRE_MINUTES.isdigit():
        ACCESS_TOKEN_EXPIRE_MINUTES = 30
else:
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM","HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer()

# JWT & Password configuration
password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    password = password.encode("utf-8")
    if len(password) > 72:
        password = hashlib.sha256(password).digest()       
    return pwd_context.hash(password.decode("utf-8"))
    

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str = Depends(bearer_scheme)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token has expired or is invalid")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Token has expired or is invalid")
    

# Dependency: get current authenticated user
def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise credentials_exception
    return user