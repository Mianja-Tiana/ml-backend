from typing import Optional, List
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)
    username: str = Field(index=True, unique=True)
    phone: Optional[str] = Field(default=None, index=True, unique=True, nullable=True)
    full_name: Optional[str] = None
    email: Optional[str] = Field(default=None, index=True, unique=True, nullable=True)
    team: Optional[str] = None
    address: Optional[str] = None
    hashed_password: str
    role: UserRole = Field(default=UserRole.USER)
    is_active: bool = Field(default=True)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    predictions: List["Prediction"] = Relationship(back_populates="user")
    feedbacks: List["Feedback"] = Relationship(back_populates="user")
    logs: List["PredictionLog"] = Relationship(back_populates="user")


class Prediction(SQLModel, table=True):
    __tablename__ = "predictions"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    input_data: str  # store JSON string of input
    prediction: int
    probability: float
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: Optional[User] = Relationship(back_populates="predictions")
    prediction_metadata: Optional["PredictionMetadata"] = Relationship(
        back_populates="prediction",
        sa_relationship_kwargs={"uselist": False}
    )
    feedbacks: List["Feedback"] = Relationship(back_populates="prediction")
    logs: List["PredictionLog"] = Relationship(back_populates="prediction")


class MLModel(SQLModel, table=True):
    __tablename__ = "mlmodels"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    version: str
    description: Optional[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    prediction_metadata: List["PredictionMetadata"] = Relationship(back_populates="model")


class PredictionMetadata(SQLModel, table=True):
    __tablename__ = "predictionmetadata"

    id: Optional[int] = Field(default=None, primary_key=True)
    prediction_id: int = Field(foreign_key="predictions.id", unique=True)
    model_id: int = Field(foreign_key="mlmodels.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    prediction: Optional[Prediction] = Relationship(back_populates="prediction_metadata")
    model: Optional[MLModel] = Relationship(back_populates="prediction_metadata")


class Feedback(SQLModel, table=True):
    __tablename__ = "feedbacks"

    id: Optional[int] = Field(default=None, primary_key=True)
    prediction_id: int = Field(foreign_key="predictions.id")
    user_id: UUID = Field(foreign_key="users.id")
    correct: Optional[bool]  # Was the prediction correct?
    comment: Optional[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    prediction: Optional[Prediction] = Relationship(back_populates="feedbacks")
    user: Optional[User] = Relationship(back_populates="feedbacks")


class PredictionLog(SQLModel, table=True):
    __tablename__ = "predictionlogs"

    id: Optional[int] = Field(default=None, primary_key=True)
    prediction_id: int = Field(foreign_key="predictions.id")
    user_id: UUID = Field(foreign_key="users.id")
    request_ip: Optional[str]
    user_agent: Optional[str]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    prediction: Optional[Prediction] = Relationship(back_populates="logs")
    user: Optional[User] = Relationship(back_populates="logs")
