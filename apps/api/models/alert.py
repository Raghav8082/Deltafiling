from uuid import uuid4
from sqlalchemy import Column, ForeignKey, String, TIMESTAMP, UUID, func
from sqlalchemy.orm import relationship

try:
    from config.database import Base
except ModuleNotFoundError:
    from apps.api.config.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    filing_id = Column(UUID(as_uuid=True), ForeignKey("filings.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    body = Column(String, nullable=False)
    status = Column(String, default="pending")
    sent_at = Column(TIMESTAMP, nullable=True)

    user = relationship("User", back_populates="alerts")
    filing = relationship("Filings", back_populates="alerts")