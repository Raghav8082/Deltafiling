from uuid import uuid4
from sqlalchemy import Column, String, UUID
from sqlalchemy.orm import relationship

try:
    from config.database import Base
except ModuleNotFoundError:
    from apps.api.config.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="user", cascade="all, delete-orphan")