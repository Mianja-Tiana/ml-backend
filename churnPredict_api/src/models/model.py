from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
from typing import Optional, List
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

# ============================================================
# USERS & ROLES
# ============================================================


# ============================================================
# USERS & ROLES
# ============================================================

# class Role(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     name: str = Field(unique=True, index=True)  # e.g. "admin", "user"
#     description: Optional[str] = None
#     created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

#     # one role has many permissions (through RolePermission)
#     permissions: List["RolePermission"] = Relationship(back_populates="role")
#     users: List["User"] = Relationship(back_populates="role")


# class Permission(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     name: str = Field(unique=True, index=True)  # e.g. "view_logs", "make_prediction"
#     description: Optional[str] = None

#     roles: List["RolePermission"] = Relationship(back_populates="permission")


# class RolePermission(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     role_id: int = Field(foreign_key="role.id")
#     permission_id: int = Field(foreign_key="permission.id")

#     role: Optional[Role] = Relationship(back_populates="permissions")
#     permission: Optional[Permission] = Relationship(back_populates="roles")


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    role: UserRole = Field(default=UserRole.USER)  # 👈 simplified role
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    predictions: List["Prediction"] = Relationship(back_populates="user")
    feedbacks: List["Feedback"] = Relationship(back_populates="user")
    logs: List["PredictionLog"] = Relationship(back_populates="user")

# ============================================================
# PREDICTIONS & ML MODELS
# ============================================================

class Prediction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    input_data: str  # store JSON string of input
    prediction: int
    probability: float
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: Optional[User] = Relationship(back_populates="predictions")
    prediction_metadata: Optional["PredictionMetadata"] = Relationship(
        back_populates="prediction",
        sa_relationship_kwargs={"uselist": False}
    )


class MLModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    version: str
    description: Optional[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    prediction_metadata: List["PredictionMetadata"] = Relationship(back_populates="model")


class PredictionMetadata(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    prediction_id: int = Field(foreign_key="prediction.id")
    model_id: int = Field(foreign_key="mlmodel.id")
    # features_used: Optional[str]  # JSON string of features used for prediction
    # feature_version: Optional[str]  # Track feature engineering version
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    prediction: Optional[Prediction] = Relationship(back_populates="prediction_metadata")
    model: Optional[MLModel] = Relationship(back_populates="prediction_metadata")


# ============================================================
# FEEDBACK & LOGGING
# ============================================================

class Feedback(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    prediction_id: int = Field(foreign_key="prediction.id")
    user_id: int = Field(foreign_key="user.id")
    correct: Optional[bool]  # Was the prediction correct?
    comment: Optional[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    prediction: Optional[Prediction] = Relationship()
    user: Optional[User] = Relationship(back_populates="feedbacks")


class PredictionLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    prediction_id: int = Field(foreign_key="prediction.id")
    user_id: int = Field(foreign_key="user.id")
    request_ip: Optional[str]
    user_agent: Optional[str]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    prediction: Optional[Prediction] = Relationship()
    user: Optional[User] = Relationship(back_populates="logs")
