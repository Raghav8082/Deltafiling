from uuid import uuid4
from sqlalchemy import Column, String, TIMESTAMP, UUID
from sqlalchemy.orm import relationship

try:
    from config.database import Base
except ModuleNotFoundError:
    from apps.api.config.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    ticker = Column(String, unique=True, nullable=False)
    company_name = Column(String, unique=True, nullable=False)
    cik = Column(String, unique=True, nullable=False)
    last_polled = Column(TIMESTAMP, nullable=True)

    subscriptions = relationship("Subscription", back_populates="company", cascade="all, delete-orphan")
    filings = relationship("Filings", back_populates="company", cascade="all, delete-orphan")