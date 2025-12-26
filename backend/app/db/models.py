"""
AI Translation Benchmark - Database Models

Author: Zoltan Tamas Toth

SQLAlchemy ORM models for storing translation runs, results, and evaluations.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Run(Base):
    """Translation run metadata."""

    __tablename__ = "runs"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    source_lang = Column(String(10), nullable=True)
    target_lang = Column(String(10), nullable=False)
    source_text = Column(Text, nullable=False)
    text_hash = Column(String(64), nullable=False, index=True)
    config_snapshot = Column(JSON, nullable=True)

    # Relationships
    translations = relationship("Translation", back_populates="run", cascade="all, delete-orphan")

    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "source_lang": self.source_lang,
            "target_lang": self.target_lang,
            "source_text": self.source_text,
            "text_hash": self.text_hash,
            "config_snapshot": self.config_snapshot,
        }


class Translation(Base):
    """Individual translation result from a provider."""

    __tablename__ = "translations"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("runs.id"), nullable=False, index=True)
    provider = Column(String(50), nullable=False)
    model = Column(String(100), nullable=False)
    latency_ms = Column(Float, nullable=False)
    output_text = Column(Text, nullable=False)
    usage_tokens = Column(Integer, nullable=True)
    raw_response = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    run = relationship("Run", back_populates="translations")
    evaluations = relationship(
        "Evaluation", back_populates="translation", cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "run_id": self.run_id,
            "provider": self.provider,
            "model": self.model,
            "latency_ms": self.latency_ms,
            "output_text": self.output_text,
            "usage_tokens": self.usage_tokens,
            "error": self.error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Evaluation(Base):
    """Evaluation metric result for a translation."""

    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, index=True)
    translation_id = Column(Integer, ForeignKey("translations.id"), nullable=False, index=True)
    metric_name = Column(String(50), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    translation = relationship("Translation", back_populates="evaluations")

    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "translation_id": self.translation_id,
            "metric_name": self.metric_name,
            "metric_value": self.metric_value,
            "details": self.details,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
