from uuid import uuid4
from sqlalchemy import (
    Column,
    Date,
    Float,
    ForeignKey,
    Integer,
    String,
    TIMESTAMP,
    UUID,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

try:
    from config.database import Base
except ModuleNotFoundError:
    from apps.api.config.database import Base


class Filings(Base):
    __tablename__ = "filings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    accession_number = Column(String, unique=True, nullable=False)
    form_type = Column(String, nullable=False)
    filing_date = Column(Date, nullable=False)
    report_date = Column(Date, nullable=False)
    primary_document = Column(String, nullable=False)
    raw_html_path = Column(String, nullable=True)
    xbrl_path = Column(String, nullable=True)
    status = Column(String, nullable=False, default="pending")
    error = Column(String, nullable=True)
    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now())

    company = relationship("Company", back_populates="filings")
    sections = relationship("Section", back_populates="filing", cascade="all, delete-orphan")
    metrics = relationship("Metrics", back_populates="filing", cascade="all, delete-orphan")
    diffs = relationship("Diff", foreign_keys="Diff.filing_id", back_populates="filing", cascade="all, delete-orphan")
    findings = relationship("Finding", back_populates="filing", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="filing", cascade="all, delete-orphan")


class Section(Base):
    __tablename__ = "sections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    filing_id = Column(UUID(as_uuid=True), ForeignKey("filings.id"), nullable=False)
    name = Column(String, nullable=False)

    __table_args__ = (
        UniqueConstraint("filing_id", "name", name="uq_filing_section_name"),
    )

    filing = relationship("Filings", back_populates="sections")
    paragraphs = relationship("Paragraphs", back_populates="section", cascade="all, delete-orphan")


class Paragraphs(Base):
    __tablename__ = "paragraphs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    section_id = Column(UUID(as_uuid=True), ForeignKey("sections.id"), nullable=False)
    position = Column(Integer, nullable=False)
    text = Column(String, nullable=False)
    text_hash = Column(String, nullable=False)

    section = relationship("Section", back_populates="paragraphs")


class Metrics(Base):
    __tablename__ = "metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    filing_id = Column(UUID(as_uuid=True), ForeignKey("filings.id"), nullable=False)
    name = Column(String, nullable=False)
    period_end = Column(Date, nullable=True)
    value = Column(Float, nullable=False)
    formula = Column(String, nullable=True)
    source_field = Column(JSONB, nullable=True)
    computed_at = Column(TIMESTAMP, default=func.now())

    filing = relationship("Filings", back_populates="metrics")


class Diff(Base):
    __tablename__ = "diffs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    filing_id = Column(UUID(as_uuid=True), ForeignKey("filings.id"), nullable=False)
    prev_filing_id = Column(UUID(as_uuid=True), ForeignKey("filings.id"), nullable=True)
    old_paragraph_id = Column(UUID(as_uuid=True), ForeignKey("paragraphs.id"), nullable=True)
    new_paragraph_id = Column(UUID(as_uuid=True), ForeignKey("paragraphs.id"), nullable=True)
    change_type = Column(String, nullable=False)
    similarity = Column(Float, nullable=False)

    filing = relationship("Filings", foreign_keys=[filing_id], back_populates="diffs")
    prev_filing = relationship("Filings", foreign_keys=[prev_filing_id])
    old_paragraph = relationship("Paragraphs", foreign_keys=[old_paragraph_id])
    new_paragraph = relationship("Paragraphs", foreign_keys=[new_paragraph_id])


class Finding(Base):
    __tablename__ = "findings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    filing_id = Column(UUID(as_uuid=True), ForeignKey("filings.id"), nullable=False)
    kind = Column(String, nullable=False)
    claim = Column(String, nullable=False)
    verdict = Column(String, nullable=False)
    severity = Column(Integer, nullable=False)
    evidence = Column(String, nullable=True)

    filing = relationship("Filings", back_populates="findings")
