import strawberry
from typing import List, Optional, Dict, Any
from datetime import datetime
from models import AdminRole, QuestionnaireStatus, QuestionType, EnquiryStatus

# GraphQL types matching our SQLAlchemy models
@strawberry.type
class UserType:
    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

@strawberry.type
class PostType:
    id: int
    title: str
    content: Optional[str] = None
    author_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

# Input types for mutations
@strawberry.input
class UserInput:
    email: str
    username: str
    full_name: Optional[str] = None

@strawberry.input
class PostInput:
    title: str
    content: Optional[str] = None
    author_id: int

# Response types
@strawberry.type
class HealthResponse:
    status: str
    timestamp: str

@strawberry.type
class HelloResponse:
    message: str

@strawberry.type
class FileInfo:
    name: str
    size: Optional[int] = None
    last_modified: Optional[str] = None

# AdminUser GraphQL types
import enum

class AdminRoleEnum(enum.Enum):
    SUPERADMIN = "superadmin"
    EDITOR = "editor"
    VIEWER = "viewer"

AdminRoleEnum = strawberry.enum(AdminRoleEnum)

@strawberry.type
class AdminUserType:
    id: str  # UUID as string
    email: str
    role: AdminRoleEnum
    created_at: datetime
    updated_at: Optional[datetime] = None

@strawberry.input
class AdminUserCreateInput:
    email: str
    password: str
    role: AdminRoleEnum = AdminRoleEnum.VIEWER

@strawberry.input
class AdminUserLoginInput:
    email: str
    password: str

@strawberry.type
class TokenResponse:
    access_token: str
    token_type: str = "bearer"
    admin_user: AdminUserType

# Questionnaire GraphQL types
import enum

class QuestionnaireStatusEnum(enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

QuestionnaireStatusEnum = strawberry.enum(QuestionnaireStatusEnum)

class QuestionTypeEnum(enum.Enum):
    SINGLE = "single"
    MULTI = "multi"
    BOOLEAN = "boolean"
    NUMBER = "number"
    TEXT = "text"
    SCALE = "scale"
    CHIPS = "chips"

QuestionTypeEnum = strawberry.enum(QuestionTypeEnum)

@strawberry.type
class QuestionOptionType:
    id: str  # UUID as string
    question_id: str  # UUID as string
    value: str
    label: str
    order_index: int
    is_other: bool

@strawberry.input
class QuestionOptionInput:
    value: str
    label: str
    order_index: int = 1
    is_other: bool = False

@strawberry.type
class QuestionType:
    id: str  # UUID as string
    questionnaire_id: str  # UUID as string
    key: str
    type: QuestionTypeEnum
    label: str
    help_text: Optional[str] = None
    required: bool
    order_index: int
    constraints: Optional[strawberry.scalars.JSON] = None
    meta: Optional[strawberry.scalars.JSON] = None
    options: List[QuestionOptionType] = strawberry.field(default_factory=list)

@strawberry.input
class QuestionInput:
    key: str
    type: QuestionTypeEnum
    label: str
    help_text: Optional[str] = None
    required: bool = False
    order_index: int = 1
    constraints: Optional[strawberry.scalars.JSON] = None
    meta: Optional[strawberry.scalars.JSON] = None
    options: Optional[List[QuestionOptionInput]] = strawberry.field(default_factory=list)

@strawberry.type
class QuestionnaireType:
    id: str  # UUID as string
    category_code: str
    title: str
    description: Optional[str] = None
    status: QuestionnaireStatusEnum
    is_active: bool
    version: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    questions: List[QuestionType] = strawberry.field(default_factory=list)

@strawberry.input
class QuestionnaireInput:
    category_code: str
    title: str
    description: Optional[str] = None
    questions: Optional[List[QuestionInput]] = strawberry.field(default_factory=list)

@strawberry.input
class QuestionnaireUpdateInput:
    title: Optional[str] = None
    description: Optional[str] = None
    questions: Optional[List[QuestionInput]] = strawberry.field(default_factory=list)

@strawberry.input
class QuestionOrderInput:
    id: str  # UUID as string
    order_index: int

# Enquiry GraphQL Types
import enum

class EnquiryStatusEnum(str, enum.Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"

EnquiryStatusGraphQL = strawberry.enum(EnquiryStatusEnum)

@strawberry.type
class EnquiryType:
    id: str
    status: EnquiryStatusGraphQL
    
    # Step 1-2 (venue + selection scope)
    venue_type: str
    venue_style: Optional[str] = None
    product_category: str
    child_category: Optional[str] = None
    
    # Profile / business fields
    legal_entity_name: Optional[str] = None
    trading_name: Optional[str] = None
    entity_type: Optional[str] = None
    abn: Optional[str] = None
    acn: Optional[str] = None
    liquor_license_number: Optional[str] = None
    outlet_type: Optional[str] = None
    business_address: Optional[str] = None
    business_city: Optional[str] = None
    business_state: Optional[str] = None
    business_postal_code: Optional[str] = None
    first_name: Optional[str] = None
    surname: Optional[str] = None
    contact_number: Optional[str] = None
    email: Optional[str] = None
    unit_number: Optional[str] = None
    street_number: Optional[str] = None
    street_name: Optional[str] = None
    referral_sourced: Optional[str] = None
    cuisine: Optional[str] = None
    outlet_style: Optional[str] = None
    apply_commercial_credit_terms: bool = False
    application_id: Optional[int] = None
    
    # Questionnaire snapshot + answers (set on submit)
    questionnaire_id: Optional[str] = None
    questionnaire_version: Optional[int] = None
    questionnaire_title: Optional[str] = None
    answers_json: Optional[strawberry.scalars.JSON] = None
    
    # Meta
    submitted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    deleted_at: Optional[datetime] = None

@strawberry.input
class EnquiryInput:
    # Step 1-2 (venue + selection scope)
    venue_type: str
    venue_style: Optional[str] = None
    product_category: str
    child_category: Optional[str] = None
    
    # Profile / business fields
    legal_entity_name: Optional[str] = None
    trading_name: Optional[str] = None
    entity_type: Optional[str] = None
    abn: Optional[str] = None
    acn: Optional[str] = None
    liquor_license_number: Optional[str] = None
    outlet_type: Optional[str] = None
    business_address: Optional[str] = None
    business_city: Optional[str] = None
    business_state: Optional[str] = None
    business_postal_code: Optional[str] = None
    first_name: Optional[str] = None
    surname: Optional[str] = None
    contact_number: Optional[str] = None
    email: Optional[str] = None
    unit_number: Optional[str] = None
    street_number: Optional[str] = None
    street_name: Optional[str] = None
    referral_sourced: Optional[str] = None
    cuisine: Optional[str] = None
    outlet_style: Optional[str] = None
    apply_commercial_credit_terms: bool = False
    application_id: Optional[int] = None

@strawberry.input
class EnquiryUpdateInput:
    # All fields optional for updates
    venue_type: Optional[str] = None
    venue_style: Optional[str] = None
    product_category: Optional[str] = None
    child_category: Optional[str] = None
    
    # Profile / business fields
    legal_entity_name: Optional[str] = None
    trading_name: Optional[str] = None
    entity_type: Optional[str] = None
    abn: Optional[str] = None
    acn: Optional[str] = None
    liquor_license_number: Optional[str] = None
    outlet_type: Optional[str] = None
    business_address: Optional[str] = None
    business_city: Optional[str] = None
    business_state: Optional[str] = None
    business_postal_code: Optional[str] = None
    first_name: Optional[str] = None
    surname: Optional[str] = None
    contact_number: Optional[str] = None
    email: Optional[str] = None
    unit_number: Optional[str] = None
    street_number: Optional[str] = None
    street_name: Optional[str] = None
    referral_sourced: Optional[str] = None
    cuisine: Optional[str] = None
    outlet_style: Optional[str] = None
    apply_commercial_credit_terms: Optional[bool] = None
    application_id: Optional[int] = None
