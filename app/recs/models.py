"""
Database models for recommendations.
"""

from sqlalchemy import Column, String, DateTime, JSON, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

Base = declarative_base()

class ActionType(enum.Enum):
    """Enum for recommendation event actions."""
    SHOWN = "shown"
    CLICKED = "clicked"
    ADDED = "added"
    PURCHASED = "purchased"

class RecommendationTemplate(Base):
    """Model for saving user recommendation templates."""
    __tablename__ = "recommendation_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(String, nullable=False, index=True)
    template_name = Column(String, nullable=True)
    items = Column(JSON, nullable=False)  # JSONB in PostgreSQL
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship to events
    events = relationship("RecommendationEvent", back_populates="template")

class RecommendationEvent(Base):
    """Model for tracking recommendation events."""
    __tablename__ = "recommendation_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(String, nullable=False, index=True)
    sku = Column(String, nullable=False, index=True)
    action = Column(Enum(ActionType), nullable=False)
    meta = Column(JSON, nullable=True)  # JSONB in PostgreSQL
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Optional foreign key to template
    template_id = Column(UUID(as_uuid=True), ForeignKey("recommendation_templates.id"), nullable=True)
    template = relationship("RecommendationTemplate", back_populates="events")

# Note: RecommendationItem is now a Pydantic schema in schemas.py, not a database model

class RecommendationLog(Base):
    """Legacy model for logging recommendation requests and responses."""
    __tablename__ = "recommendation_logs"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String(255))
    query = Column(String, nullable=False)
    response = Column(JSON)
    processing_time = Column(String)
    created_at = Column(DateTime, default=func.now())