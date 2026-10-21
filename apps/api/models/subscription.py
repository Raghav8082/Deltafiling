from sqlalchemy import Column, ForeignKey, TIMESTAMP, UUID, func
from sqlalchemy.orm import relationship

try:
    from config.database import Base
except ModuleNotFoundError:
    from apps.api.config.database import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), primary_key=True)
    created_at = Column(TIMESTAMP, default=func.now())

    user = relationship("User", back_populates="subscriptions")
    company = relationship("Company", back_populates="subscriptions")