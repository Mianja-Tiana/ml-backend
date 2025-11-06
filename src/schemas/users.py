from sqlalchemy import Column, String, Boolean, Date
from sqlalchemy.dialects.postgresql import UUID

import uuid
from db.database import Base
from datetime import date

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone = Column(String, unique=True, index=True, nullable=False)    
    full_name = Column(String)
    email=Column(String, unique=True, index=True, nullable=True)
    team = Column(String)
    address = Column(String)
    password = Column(String)
    role = Column(String)
    created_at = Column(Date, default=date.today)
    updated_at = Column(Date, default=date.today)
    is_active = Column(Boolean, default=True)