from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from models.model import User, UserRole
from controllers.middleware.auth import get_password_hash, get_current_user
from db.database import get_session
from schemas.schema import UserCreate

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/create-admin", status_code=201)
def create_admin_user(
    user_in: UserCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Ensure only admins can create admin accounts
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only")

    # Check if username already exists
    user_exists = session.exec(
        select(User).where(User.username == user_in.username)).first()

    if user_exists:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    new_admin = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        role=UserRole.ADMIN,
    )

    session.add(new_admin)
    session.commit()
    session.refresh(new_admin)

    return {"message":"Admin account created successfully", "user": new_admin.username}
