from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, Boolean, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from database import Base

class AdminRole(str, enum.Enum):
    SUPERADMIN = "superadmin"
    EDITOR = "editor"
    VIEWER = "viewer"

class QuestionnaireStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class QuestionType(str, enum.Enum):
    SINGLE = "single"
    MULTI = "multi"
    BOOLEAN = "boolean"
    NUMBER = "number"
    TEXT = "text"
    SCALE = "scale"
    CHIPS = "chips"

class EnquiryStatus(str, enum.Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    content = Column(Text, nullable=True)
    author_id = Column(Integer, nullable=False)  # Foreign key to users.id
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(AdminRole), nullable=False, default=AdminRole.VIEWER)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Questionnaire(Base):
    __tablename__ = "questionnaires"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    category_code = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(QuestionnaireStatus), nullable=False, default=QuestionnaireStatus.DRAFT)
    is_active = Column(Boolean, nullable=False, default=False)
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    questions = relationship("Question", back_populates="questionnaire", cascade="all, delete-orphan")

    # Partial unique index for active questionnaires per category
    __table_args__ = (
        Index('uniq_active_questionnaire_per_category', 'category_code',
              postgresql_where=(status == QuestionnaireStatus.PUBLISHED) &
                              (is_active == True) &
                              (deleted_at.is_(None))),
    )

class Question(Base):
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    questionnaire_id = Column(UUID(as_uuid=True), ForeignKey("questionnaires.id", ondelete="CASCADE"), nullable=False)
    key = Column(String, nullable=False)
    type = Column(Enum(QuestionType), nullable=False)
    label = Column(String, nullable=False)
    help_text = Column(Text, nullable=True)
    required = Column(Boolean, nullable=False, default=False)
    order_index = Column(Integer, nullable=False, default=1)
    constraints = Column(JSONB, nullable=True)
    meta = Column(JSONB, nullable=True)

    # Relationships
    questionnaire = relationship("Questionnaire", back_populates="questions")
    options = relationship("QuestionOption", back_populates="question", cascade="all, delete-orphan")

    # Unique constraint for key per questionnaire
    __table_args__ = (
        UniqueConstraint('questionnaire_id', 'key', name='uq_question_key_per_questionnaire'),
    )

class QuestionOption(Base):
    __tablename__ = "question_options"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    value = Column(String, nullable=False)
    label = Column(String, nullable=False)
    order_index = Column(Integer, nullable=False, default=1)
    is_other = Column(Boolean, nullable=False, default=False)

    # Relationships
    question = relationship("Question", back_populates="options")

class Enquiry(Base):
    __tablename__ = "enquiries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    status = Column(Enum(EnquiryStatus), nullable=False, default=EnquiryStatus.PENDING)

    # Step 1-2 (venue + selection scope)
    venue_type = Column(String, nullable=False)
    venue_style = Column(String, nullable=True)
    product_category = Column(String, nullable=False)
    child_category = Column(String, nullable=True)

    # Profile / business fields
    legal_entity_name = Column(String, nullable=True)
    trading_name = Column(String, nullable=True)
    entity_type = Column(String, nullable=True)
    abn = Column(String, nullable=True)
    acn = Column(String, nullable=True)
    liquor_license_number = Column(String, nullable=True)
    outlet_type = Column(String, nullable=True)
    business_address = Column(String, nullable=True)
    business_city = Column(String, nullable=True)
    business_state = Column(String, nullable=True)
    business_postal_code = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    surname = Column(String, nullable=True)
    contact_number = Column(String, nullable=True)
    email = Column(String, nullable=True, unique=True)
    unit_number = Column(String, nullable=True)
    street_number = Column(String, nullable=True)
    street_name = Column(String, nullable=True)
    referral_sourced = Column(String, nullable=True)
    cuisine = Column(String, nullable=True)
    outlet_style = Column(String, nullable=True)
    apply_commercial_credit_terms = Column(Boolean, nullable=False, default=False)
    application_id = Column(Integer, nullable=True)

    # Questionnaire snapshot + answers (set on submit)
    questionnaire_id = Column(UUID(as_uuid=True), nullable=True)
    questionnaire_version = Column(Integer, nullable=True)
    questionnaire_title = Column(String, nullable=True)
    answers_json = Column(JSONB, nullable=True)

    # SF payload snapshot (store only, never expose in GraphQL)
    salesforce_payload_json = Column(JSONB, nullable=True)

    # Meta
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Indexes
    __table_args__ = (
        Index('idx_enquiry_status', 'status'),
        Index('idx_enquiry_venue_type', 'venue_type'),
        Index('idx_enquiry_venue_style', 'venue_style'),
        Index('idx_enquiry_email', 'email'),
        Index('idx_enquiry_created_at', 'created_at'),
    )
