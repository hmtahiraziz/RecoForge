from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from models import AdminRole, QuestionnaireStatus, QuestionType, EnquiryStatus

# User schemas
class UserBase(BaseModel):
    email: str
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    full_name: Optional[str] = None

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Post schemas
class PostBase(BaseModel):
    title: str
    content: Optional[str] = None

class PostCreate(PostBase):
    author_id: int

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class Post(PostBase):
    id: int
    author_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# AdminUser schemas
class AdminUserBase(BaseModel):
    email: EmailStr
    role: AdminRole = AdminRole.VIEWER

class AdminUserCreate(AdminUserBase):
    password: str

class AdminUserLogin(BaseModel):
    email: EmailStr
    password: str

class AdminUserResponse(AdminUserBase):
    id: str  # UUID as string
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    admin_user: AdminUserResponse

# Questionnaire schemas
class QuestionOptionBase(BaseModel):
    value: str
    label: str
    order_index: int = 1
    is_other: bool = False

class QuestionOptionCreate(QuestionOptionBase):
    pass

class QuestionOptionUpdate(QuestionOptionBase):
    pass

class QuestionOption(QuestionOptionBase):
    id: str  # UUID as string
    question_id: str  # UUID as string

    class Config:
        from_attributes = True

class QuestionBase(BaseModel):
    key: str
    type: QuestionType
    label: str
    help_text: Optional[str] = None
    required: bool = False
    order_index: int = 1
    constraints: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = None

class QuestionCreate(QuestionBase):
    options: Optional[List[QuestionOptionCreate]] = []

class QuestionUpdate(QuestionBase):
    options: Optional[List[QuestionOptionCreate]] = None

class Question(QuestionBase):
    id: str  # UUID as string
    questionnaire_id: str  # UUID as string
    options: List[QuestionOption] = []

    class Config:
        from_attributes = True

class QuestionnaireBase(BaseModel):
    category_code: str
    title: str
    description: Optional[str] = None

class QuestionnaireCreate(QuestionnaireBase):
    questions: Optional[List[QuestionCreate]] = []

class QuestionnaireUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class Questionnaire(QuestionnaireBase):
    id: str  # UUID as string
    status: QuestionnaireStatus
    is_active: bool
    version: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    questions: List[Question] = []

    class Config:
        from_attributes = True

class QuestionOrder(BaseModel):
    id: str  # UUID as string
    order_index: int

# Enquiry schemas
class EnquiryBase(BaseModel):
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

class EnquiryCreate(EnquiryBase):
    pass

class EnquiryUpdate(EnquiryBase):
    # All fields optional for updates
    venue_type: Optional[str] = None
    product_category: Optional[str] = None

class Enquiry(EnquiryBase):
    id: str  # UUID as string
    status: EnquiryStatus
    questionnaire_id: Optional[str] = None  # UUID as string
    questionnaire_version: Optional[int] = None
    questionnaire_title: Optional[str] = None
    answers_json: Optional[Dict[str, Any]] = None
    submitted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class EnquirySubmit(BaseModel):
    questionnaire_id: str  # UUID as string
    questionnaire_version: int
    questionnaire_title: str
    answers: Dict[str, Any]  # JSON answers
