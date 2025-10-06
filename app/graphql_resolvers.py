import strawberry
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import User, Post, AdminUser, AdminRole, Questionnaire, Question, QuestionOption, Enquiry, QuestionnaireStatus, QuestionType, EnquiryStatus
from graphql_types import UserType, PostType, UserInput, PostInput, HealthResponse, HelloResponse, FileInfo, AdminUserType, AdminUserCreateInput, AdminUserLoginInput, TokenResponse, AdminRoleEnum, QuestionnaireType, QuestionnaireInput, QuestionnaireUpdateInput, QuestionType as QuestionTypeGraphQL, QuestionInput, QuestionOptionType, QuestionOptionInput, QuestionOrderInput, QuestionnaireStatusEnum, QuestionTypeEnum, EnquiryType, EnquiryInput, EnquiryUpdateInput, EnquiryStatusGraphQL
from auth_utils import get_password_hash, authenticate_admin_user, create_access_token, verify_token, check_role_permission
from fastapi import HTTPException, status
import os
import boto3
from botocore.exceptions import ClientError
from datetime import datetime

@strawberry.type
class Query:
    @strawberry.field
    async def health(self) -> HealthResponse:
        """Health check endpoint"""
        return HealthResponse(
            status="OK",
            timestamp=datetime.utcnow().isoformat()
        )

    @strawberry.field
    async def hello(self) -> HelloResponse:
        """Hello message"""
        return HelloResponse(message="Hello from GraphQL!")

    @strawberry.field
    async def users(self, skip: int = 0, limit: int = 100) -> List[UserType]:
        """Get all users"""
        async for db in get_db():
            result = await db.execute(select(User).offset(skip).limit(limit))
            users = result.scalars().all()
            return users

    @strawberry.field
    async def user(self, user_id: int) -> Optional[UserType]:
        """Get a specific user"""
        async for db in get_db():
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            return user

    @strawberry.field
    async def posts(self, skip: int = 0, limit: int = 100) -> List[PostType]:
        """Get all posts"""
        async for db in get_db():
            result = await db.execute(select(Post).offset(skip).limit(limit))
            posts = result.scalars().all()
            return posts

    @strawberry.field
    async def post(self, post_id: int) -> Optional[PostType]:
        """Get a specific post"""
        async for db in get_db():
            result = await db.execute(select(Post).where(Post.id == post_id))
            post = result.scalar_one_or_none()
            return post

    @strawberry.field
    async def files(self) -> List[FileInfo]:
        """List files from S3 bucket"""
        bucket_name = os.getenv('FILES_BUCKET')

        if not bucket_name:
            return [FileInfo(name="S3 bucket not configured")]

        try:
            s3_client = boto3.client('s3', region_name=os.getenv('AWS_REGION', 'us-east-1'))
            response = s3_client.list_objects_v2(Bucket=bucket_name)
            files = []

            if 'Contents' in response:
                for obj in response['Contents']:
                    files.append(FileInfo(
                        name=obj['Key'],
                        size=obj['Size'],
                        last_modified=obj['LastModified'].isoformat()
                    ))

            return files if files else [FileInfo(name="No files found")]

        except ClientError as e:
            return [FileInfo(name=f"S3 error: {str(e)}")]

    @strawberry.field
    async def me(self, info) -> Optional[AdminUserType]:
        """Get current logged-in admin user"""
        try:
            token = info.context.get("token")
            if not token:
                return None
                
            payload = verify_token(token)
            admin_id = payload.get("sub")
            
            if not admin_id:
                return None
                
            async for db in get_db():
                result = await db.execute(select(AdminUser).where(AdminUser.id == admin_id))
                admin_user = result.scalar_one_or_none()
                
                if not admin_user:
                    return None
                
                return AdminUserType(
                    id=str(admin_user.id),
                    email=admin_user.email,
                    role=AdminRoleEnum(admin_user.role.value),
                    created_at=admin_user.created_at,
                    updated_at=admin_user.updated_at
                )
        except Exception:
            return None

    # Questionnaire Queries
    @strawberry.field
    async def questionnaires(self, category: Optional[str] = None, status: Optional[QuestionnaireStatusEnum] = None, include_deleted: bool = False) -> List[QuestionnaireType]:
        """Get questionnaires with optional filtering"""
        async for db in get_db():
            from sqlalchemy.orm import selectinload
            
            query = select(Questionnaire).options(
                selectinload(Questionnaire.questions).selectinload(Question.options)
            )
            
            if not include_deleted:
                query = query.where(Questionnaire.deleted_at.is_(None))
            
            if category:
                query = query.where(Questionnaire.category_code == category)
            
            if status:
                query = query.where(Questionnaire.status == QuestionnaireStatus(status.value))
            
            result = await db.execute(query)
            questionnaires = result.scalars().all()
            
            # Convert questionnaires to GraphQL types
            questionnaire_list = []
            for q in questionnaires:
                # Convert questions to GraphQL types
                questions_list = []
                for question in q.questions:
                    options_list = []
                    for option in question.options:
                        options_list.append(QuestionOptionType(
                            id=str(option.id),
                            question_id=str(option.question_id),
                            value=option.value,
                            label=option.label,
                            order_index=option.order_index,
                            is_other=option.is_other
                        ))
                    
                    question_type = QuestionTypeGraphQL(
                        id=str(question.id),
                        questionnaire_id=str(question.questionnaire_id),
                        key=question.key,
                        type=QuestionTypeEnum(question.type.value),
                        label=question.label,
                        help_text=question.help_text,
                        required=question.required,
                        order_index=question.order_index,
                        constraints=question.constraints,
                        meta=question.meta,
                        options=options_list
                    )
                    questions_list.append(question_type)
                
                questionnaire_list.append(QuestionnaireType(
                    id=str(q.id),
                    category_code=q.category_code,
                    title=q.title,
                    description=q.description,
                    status=QuestionnaireStatusEnum(q.status.value),
                    is_active=q.is_active,
                    version=q.version,
                    created_at=q.created_at,
                    updated_at=q.updated_at,
                    published_at=q.published_at,
                    deleted_at=q.deleted_at,
                    questions=questions_list
                ))
            
            return questionnaire_list

    @strawberry.field
    async def questionnaire(self, id: str) -> Optional[QuestionnaireType]:
        """Get a specific questionnaire by ID"""
        async for db in get_db():
            from sqlalchemy.orm import selectinload
            
            # Load questionnaire with questions and their options
            result = await db.execute(
                select(Questionnaire)
                .options(
                    selectinload(Questionnaire.questions).selectinload(Question.options)
                )
                .where(Questionnaire.id == id)
            )
            q = result.scalar_one_or_none()
            
            if not q:
                return None
            
            # Convert questions to GraphQL types
            questions_list = []
            for question in q.questions:
                options_list = []
                for option in question.options:
                    options_list.append(QuestionOptionType(
                        id=str(option.id),
                        question_id=str(option.question_id),
                        value=option.value,
                        label=option.label,
                        order_index=option.order_index,
                        is_other=option.is_other
                    ))
                
                question_type = QuestionTypeGraphQL(
                    id=str(question.id),
                    questionnaire_id=str(question.questionnaire_id),
                    key=question.key,
                    type=QuestionTypeEnum(question.type.value),
                    label=question.label,
                    help_text=question.help_text,
                    required=question.required,
                    order_index=question.order_index,
                    constraints=question.constraints,
                    meta=question.meta,
                    options=options_list
                )
                questions_list.append(question_type)
            
            return QuestionnaireType(
                id=str(q.id),
                category_code=q.category_code,
                title=q.title,
                description=q.description,
                status=QuestionnaireStatusEnum(q.status.value),
                is_active=q.is_active,
                version=q.version,
                created_at=q.created_at,
                updated_at=q.updated_at,
                published_at=q.published_at,
                deleted_at=q.deleted_at,
                questions=questions_list
            )

    @strawberry.field
    async def active_questionnaire_by_category(self, category: str) -> Optional[QuestionnaireType]:
        """Get the latest published questionnaire for a specific category"""
        async for db in get_db():
            result = await db.execute(
                select(Questionnaire).where(
                    Questionnaire.category_code == category,
                    Questionnaire.status == QuestionnaireStatus.PUBLISHED,
                    Questionnaire.deleted_at.is_(None)
                ).order_by(Questionnaire.published_at.desc(), Questionnaire.version.desc()).limit(1)
            )
            q = result.scalar_one_or_none()
            
            if not q:
                return None
            
            return QuestionnaireType(
                id=str(q.id),
                category_code=q.category_code,
                title=q.title,
                description=q.description,
                status=QuestionnaireStatusEnum(q.status.value),
                is_active=q.is_active,
                version=q.version,
                created_at=q.created_at,
                updated_at=q.updated_at,
                published_at=q.published_at,
                deleted_at=q.deleted_at,
                questions=[]
            )

    @strawberry.field
    async def enquiry_public(self, id: str) -> Optional[EnquiryType]:
        """Get enquiry by ID (public, no auth required)"""
        async for db in get_db():
            result = await db.execute(select(Enquiry).where(Enquiry.id == id, Enquiry.deleted_at.is_(None)))
            enquiry = result.scalar_one_or_none()
            
            if not enquiry:
                return None
            
            return EnquiryType(
                id=str(enquiry.id),
                status=EnquiryStatusGraphQL(enquiry.status.value),
                venue_type=enquiry.venue_type,
                venue_style=enquiry.venue_style,
                product_category=enquiry.product_category,
                child_category=enquiry.child_category,
                legal_entity_name=enquiry.legal_entity_name,
                trading_name=enquiry.trading_name,
                entity_type=enquiry.entity_type,
                abn=enquiry.abn,
                acn=enquiry.acn,
                liquor_license_number=enquiry.liquor_license_number,
                outlet_type=enquiry.outlet_type,
                business_address=enquiry.business_address,
                business_city=enquiry.business_city,
                business_state=enquiry.business_state,
                business_postal_code=enquiry.business_postal_code,
                first_name=enquiry.first_name,
                surname=enquiry.surname,
                contact_number=enquiry.contact_number,
                email=enquiry.email,
                unit_number=enquiry.unit_number,
                street_number=enquiry.street_number,
                street_name=enquiry.street_name,
                referral_sourced=enquiry.referral_sourced,
                cuisine=enquiry.cuisine,
                outlet_style=enquiry.outlet_style,
                apply_commercial_credit_terms=enquiry.apply_commercial_credit_terms,
                application_id=enquiry.application_id,
                questionnaire_id=str(enquiry.questionnaire_id) if enquiry.questionnaire_id else None,
                questionnaire_version=enquiry.questionnaire_version,
                questionnaire_title=enquiry.questionnaire_title,
                answers_json=enquiry.answers_json,
                submitted_at=enquiry.submitted_at,
                created_at=enquiry.created_at,
                updated_at=enquiry.updated_at,
                ip_address=enquiry.ip_address,
                user_agent=enquiry.user_agent,
                deleted_at=enquiry.deleted_at
            )

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_user(self, user_input: UserInput) -> UserType:
        """Create a new user"""
        async for db in get_db():
            db_user = User(
                email=user_input.email,
                username=user_input.username,
                full_name=user_input.full_name
            )
            db.add(db_user)
            await db.commit()
            await db.refresh(db_user)
            return db_user

    @strawberry.mutation
    async def create_post(self, post_input: PostInput) -> PostType:
        """Create a new post"""
        async for db in get_db():
            db_post = Post(
                title=post_input.title,
                content=post_input.content,
                author_id=post_input.author_id
            )
            db.add(db_post)
            await db.commit()
            await db.refresh(db_post)
            return db_post

    @strawberry.mutation
    async def update_user(self, user_id: int, user_input: UserInput) -> Optional[UserType]:
        """Update a user"""
        async for db in get_db():
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()

            if not user:
                return None

            user.email = user_input.email
            user.username = user_input.username
            user.full_name = user_input.full_name

            await db.commit()
            await db.refresh(user)
            return user

    @strawberry.mutation
    async def delete_user(self, user_id: int) -> bool:
        """Delete a user"""
        async for db in get_db():
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()

            if not user:
                return False

            await db.delete(user)
            await db.commit()
            return True

    @strawberry.mutation
    async def register_admin_user(self, admin_input: AdminUserCreateInput, info) -> AdminUserType:
        """Register a new admin user (superadmin only)"""
        try:
            # Get token from context
            token = info.context.get("token")
            if not token:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No token provided")
                
            # Verify the token and get current user
            payload = verify_token(token)
            current_admin_id = payload.get("sub")
            
            if not current_admin_id:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
            
            async for db in get_db():
                # Get current admin user to check role
                result = await db.execute(select(AdminUser).where(AdminUser.id == current_admin_id))
                current_admin = result.scalar_one_or_none()
                
                if not current_admin or current_admin.role != AdminRole.SUPERADMIN:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only superadmin can register new admin users")
                
                # Check if email already exists
                existing_result = await db.execute(select(AdminUser).where(AdminUser.email == admin_input.email))
                if existing_result.scalar_one_or_none():
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
                
                # Create new admin user
                db_admin = AdminUser(
                    email=admin_input.email,
                    password_hash=get_password_hash(admin_input.password),
                    role=AdminRole(admin_input.role.value)
                )
                db.add(db_admin)
                await db.commit()
                await db.refresh(db_admin)
                
                return AdminUserType(
                    id=str(db_admin.id),
                    email=db_admin.email,
                    role=AdminRoleEnum(db_admin.role.value),
                    created_at=db_admin.created_at,
                    updated_at=db_admin.updated_at
                )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    @strawberry.mutation
    async def login_admin_user(self, login_input: AdminUserLoginInput) -> TokenResponse:
        """Login admin user and return JWT token"""
        async for db in get_db():
            admin_user = await authenticate_admin_user(login_input.email, login_input.password, db)
            
            if not admin_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Create access token
            access_token = create_access_token(data={"sub": str(admin_user.id)})
            
            return TokenResponse(
                access_token=access_token,
                token_type="bearer",
                admin_user=AdminUserType(
                    id=str(admin_user.id),
                    email=admin_user.email,
                    role=AdminRoleEnum(admin_user.role.value),
                    created_at=admin_user.created_at,
                    updated_at=admin_user.updated_at
                )
            )

    # Questionnaire Mutations
    @strawberry.mutation
    async def create_questionnaire(self, input: QuestionnaireInput, info) -> QuestionnaireType:
        """Create a new questionnaire (editor+)"""
        # Get token from context
        token = info.context.get("token")
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No token provided")
            
        # Verify token and check permissions
        payload = verify_token(token)
        admin_id = payload.get("sub")
        
        async for db in get_db():
            result = await db.execute(select(AdminUser).where(AdminUser.id == admin_id))
            admin_user = result.scalar_one_or_none()
            
            if not admin_user:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
            
            if not check_role_permission(admin_user.role, AdminRole.EDITOR):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
            
            # Check if a questionnaire with this category already exists
            existing_result = await db.execute(
                select(Questionnaire).where(
                    Questionnaire.category_code == input.category_code,
                    Questionnaire.deleted_at.is_(None)
                )
            )
            existing_questionnaire = existing_result.scalar_one_or_none()
            
            if existing_questionnaire:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail=f"A questionnaire with type '{input.category_code}' already exists"
                )
            
            # Create questionnaire
            questionnaire = Questionnaire(
                category_code=input.category_code,
                title=input.title,
                description=input.description,
                status=QuestionnaireStatus.DRAFT
            )
            db.add(questionnaire)
            await db.commit()
            await db.refresh(questionnaire)
            
            # Create questions if provided
            if input.questions:
                for question_input in input.questions:
                    question = Question(
                        questionnaire_id=questionnaire.id,
                        key=question_input.key,
                        type=QuestionType(question_input.type.value),
                        label=question_input.label,
                        help_text=question_input.help_text,
                        required=question_input.required,
                        order_index=question_input.order_index,
                        constraints=question_input.constraints,
                        meta=question_input.meta
                    )
                    db.add(question)
                    await db.commit()
                    await db.refresh(question)
                    
                    # Create options if provided
                    if question_input.options:
                        for option_input in question_input.options:
                            option = QuestionOption(
                                question_id=question.id,
                                value=option_input.value,
                                label=option_input.label,
                                order_index=option_input.order_index,
                                is_other=option_input.is_other
                            )
                            db.add(option)
                        await db.commit()
            
            return QuestionnaireType(
                id=str(questionnaire.id),
                category_code=questionnaire.category_code,
                title=questionnaire.title,
                description=questionnaire.description,
                status=QuestionnaireStatusEnum(questionnaire.status.value),
                is_active=questionnaire.is_active,
                version=questionnaire.version,
                created_at=questionnaire.created_at,
                updated_at=questionnaire.updated_at,
                published_at=questionnaire.published_at,
                deleted_at=questionnaire.deleted_at,
                questions=[]
            )

    @strawberry.mutation
    async def update_questionnaire(self, id: str, input: QuestionnaireUpdateInput, info) -> Optional[QuestionnaireType]:
        """Update a questionnaire (editor+)"""
        token = info.context.get("token")
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No token provided")
            
        payload = verify_token(token)
        admin_id = payload.get("sub")
        
        async for db in get_db():
            result = await db.execute(select(AdminUser).where(AdminUser.id == admin_id))
            admin_user = result.scalar_one_or_none()
            
            if not admin_user:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
            
            if not check_role_permission(admin_user.role, AdminRole.EDITOR):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
            
            # Get questionnaire
            result = await db.execute(select(Questionnaire).where(Questionnaire.id == id))
            questionnaire = result.scalar_one_or_none()
            
            if not questionnaire:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Questionnaire not found")
            
            # If questionnaire is published, set it back to draft when editing
            if questionnaire.status == QuestionnaireStatus.PUBLISHED:
                questionnaire.status = QuestionnaireStatus.DRAFT
                questionnaire.is_active = False  # Deactivate when going back to draft
            
            # Update fields
            if input.title is not None:
                questionnaire.title = input.title
            if input.description is not None:
                questionnaire.description = input.description
            
            # Update questions if provided
            if input.questions is not None:
                # Delete existing questions and their options
                existing_questions_result = await db.execute(select(Question).where(Question.questionnaire_id == questionnaire.id))
                existing_questions = existing_questions_result.scalars().all()
                for question in existing_questions:
                    # Delete options first
                    existing_options_result = await db.execute(select(QuestionOption).where(QuestionOption.question_id == question.id))
                    existing_options = existing_options_result.scalars().all()
                    for option in existing_options:
                        await db.delete(option)
                    # Delete question
                    await db.delete(question)
                
                # Commit the deletions first
                await db.commit()
                
                # Add new questions
                for question_input in input.questions:
                    question = Question(
                        questionnaire_id=questionnaire.id,
                        key=question_input.key,
                        type=QuestionType(question_input.type.value),
                        label=question_input.label,
                        help_text=question_input.help_text,
                        required=question_input.required,
                        order_index=question_input.order_index,
                        constraints=question_input.constraints,
                        meta=question_input.meta
                    )
                    db.add(question)
                    await db.flush()  # Flush to get the question ID
                    
                    # Add options for this question
                    if question_input.options:
                        for option_input in question_input.options:
                            option = QuestionOption(
                                question_id=question.id,
                                value=option_input.value,
                                label=option_input.label,
                                order_index=option_input.order_index,
                                is_other=option_input.is_other
                            )
                            db.add(option)
            
            await db.commit()
            await db.refresh(questionnaire)
            
            return QuestionnaireType(
                id=str(questionnaire.id),
                category_code=questionnaire.category_code,
                title=questionnaire.title,
                description=questionnaire.description,
                status=QuestionnaireStatusEnum(questionnaire.status.value),
                is_active=questionnaire.is_active,
                version=questionnaire.version,
                created_at=questionnaire.created_at,
                updated_at=questionnaire.updated_at,
                published_at=questionnaire.published_at,
                deleted_at=questionnaire.deleted_at,
                questions=[]
            )

    @strawberry.mutation
    async def delete_questionnaire(self, id: str, info) -> bool:
        """Delete a questionnaire (soft delete for drafts only) (editor+)"""
        token = info.context.get("token")
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No token provided")
            
        payload = verify_token(token)
        admin_id = payload.get("sub")
        
        async for db in get_db():
            result = await db.execute(select(AdminUser).where(AdminUser.id == admin_id))
            admin_user = result.scalar_one_or_none()
            
            if not admin_user:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
            
            if not check_role_permission(admin_user.role, AdminRole.EDITOR):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
            
            # Get questionnaire
            result = await db.execute(select(Questionnaire).where(Questionnaire.id == id))
            questionnaire = result.scalar_one_or_none()
            
            if not questionnaire:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Questionnaire not found")
            
            if questionnaire.status != QuestionnaireStatus.DRAFT:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only draft questionnaires can be deleted")
            
            # Soft delete
            questionnaire.deleted_at = datetime.utcnow()
            await db.commit()
            
            return True

    @strawberry.mutation
    async def publish_questionnaire(self, id: str, info) -> Optional[QuestionnaireType]:
        """Publish a questionnaire (editor+)"""
        token = info.context.get("token")
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No token provided")
            
        payload = verify_token(token)
        admin_id = payload.get("sub")
        
        async for db in get_db():
            result = await db.execute(select(AdminUser).where(AdminUser.id == admin_id))
            admin_user = result.scalar_one_or_none()
            
            if not admin_user:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
            
            if not check_role_permission(admin_user.role, AdminRole.EDITOR):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
            
            # Get questionnaire
            result = await db.execute(select(Questionnaire).where(Questionnaire.id == id))
            questionnaire = result.scalar_one_or_none()
            
            if not questionnaire:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Questionnaire not found")
            
            if questionnaire.status != QuestionnaireStatus.DRAFT:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only draft questionnaires can be published")
            
            # Deactivate any other active questionnaire in the same category
            other_active_result = await db.execute(
                select(Questionnaire).where(
                    Questionnaire.category_code == questionnaire.category_code,
                    Questionnaire.status == QuestionnaireStatus.PUBLISHED,
                    Questionnaire.is_active == True,
                    Questionnaire.deleted_at.is_(None)
                )
            )
            other_active = other_active_result.scalars().all()
            for other in other_active:
                other.is_active = False
            
            # Get max version for this category
            max_version_result = await db.execute(
                select(Questionnaire.version).where(
                    Questionnaire.category_code == questionnaire.category_code,
                    Questionnaire.status == QuestionnaireStatus.PUBLISHED,
                    Questionnaire.deleted_at.is_(None)
                ).order_by(Questionnaire.version.desc()).limit(1)
            )
            max_version = max_version_result.scalar_one_or_none() or 0
            
            # Publish questionnaire
            questionnaire.status = QuestionnaireStatus.PUBLISHED
            questionnaire.is_active = True
            questionnaire.published_at = datetime.utcnow()
            questionnaire.version = max_version + 1
            
            await db.commit()
            await db.refresh(questionnaire)
            
            try:
                return QuestionnaireType(
                    id=str(questionnaire.id),
                    category_code=questionnaire.category_code,
                    title=questionnaire.title,
                    description=questionnaire.description,
                    status=QuestionnaireStatusEnum(questionnaire.status.value),
                    is_active=questionnaire.is_active,
                    version=questionnaire.version,
                    created_at=questionnaire.created_at,
                    updated_at=questionnaire.updated_at,
                    published_at=questionnaire.published_at,
                    deleted_at=questionnaire.deleted_at,
                    questions=[]
                )
            except Exception as e:
                print(f"Error creating QuestionnaireType: {e}")
                print(f"Questionnaire status: {questionnaire.status}")
                print(f"Questionnaire status value: {questionnaire.status.value}")
                raise e

    @strawberry.mutation
    async def activate_questionnaire(self, id: str, info) -> Optional[QuestionnaireType]:
        """Activate a published questionnaire (editor+)"""
        token = info.context.get("token")
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No token provided")
            
        payload = verify_token(token)
        admin_id = payload.get("sub")
        
        async for db in get_db():
            result = await db.execute(select(AdminUser).where(AdminUser.id == admin_id))
            admin_user = result.scalar_one_or_none()
            
            if not admin_user:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
            
            if not check_role_permission(admin_user.role, AdminRole.EDITOR):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
            
            # Get questionnaire
            result = await db.execute(select(Questionnaire).where(Questionnaire.id == id))
            questionnaire = result.scalar_one_or_none()
            
            if not questionnaire:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Questionnaire not found")
            
            if questionnaire.status != QuestionnaireStatus.PUBLISHED:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only published questionnaires can be activated")
            
            # Deactivate any other active questionnaire in the same category
            other_active_result = await db.execute(
                select(Questionnaire).where(
                    Questionnaire.category_code == questionnaire.category_code,
                    Questionnaire.status == QuestionnaireStatus.PUBLISHED,
                    Questionnaire.is_active == True,
                    Questionnaire.deleted_at.is_(None)
                )
            )
            other_active = other_active_result.scalars().all()
            for other in other_active:
                other.is_active = False
            
            # Activate questionnaire
            questionnaire.is_active = True
            await db.commit()
            await db.refresh(questionnaire)
            
            return QuestionnaireType(
                id=str(questionnaire.id),
                category_code=questionnaire.category_code,
                title=questionnaire.title,
                description=questionnaire.description,
                status=QuestionnaireStatusEnum(questionnaire.status.value),
                is_active=questionnaire.is_active,
                version=questionnaire.version,
                created_at=questionnaire.created_at,
                updated_at=questionnaire.updated_at,
                published_at=questionnaire.published_at,
                deleted_at=questionnaire.deleted_at,
                questions=[]
            )

    @strawberry.mutation
    async def deactivate_questionnaire(self, id: str, info) -> Optional[QuestionnaireType]:
        """Deactivate a questionnaire (editor+)"""
        token = info.context.get("token")
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No token provided")
            
        payload = verify_token(token)
        admin_id = payload.get("sub")
        
        async for db in get_db():
            result = await db.execute(select(AdminUser).where(AdminUser.id == admin_id))
            admin_user = result.scalar_one_or_none()
            
            if not admin_user:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
            
            if not check_role_permission(admin_user.role, AdminRole.EDITOR):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
            
            # Get questionnaire
            result = await db.execute(select(Questionnaire).where(Questionnaire.id == id))
            questionnaire = result.scalar_one_or_none()
            
            if not questionnaire:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Questionnaire not found")
            
            if questionnaire.status != QuestionnaireStatus.PUBLISHED:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only published questionnaires can be deactivated")
            
            # Deactivate questionnaire
            questionnaire.is_active = False
            await db.commit()
            await db.refresh(questionnaire)
            
            return QuestionnaireType(
                id=str(questionnaire.id),
                category_code=questionnaire.category_code,
                title=questionnaire.title,
                description=questionnaire.description,
                status=QuestionnaireStatusEnum(questionnaire.status.value),
                is_active=questionnaire.is_active,
                version=questionnaire.version,
                created_at=questionnaire.created_at,
                updated_at=questionnaire.updated_at,
                published_at=questionnaire.published_at,
                deleted_at=questionnaire.deleted_at,
                questions=[]
            )

    @strawberry.mutation
    async def clone_questionnaire(self, id: str, info) -> Optional[QuestionnaireType]:
        """Clone a questionnaire (editor+)"""
        token = info.context.get("token")
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No token provided")
            
        payload = verify_token(token)
        admin_id = payload.get("sub")
        
        async for db in get_db():
            result = await db.execute(select(AdminUser).where(AdminUser.id == admin_id))
            admin_user = result.scalar_one_or_none()
            
            if not admin_user:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
            
            if not check_role_permission(admin_user.role, AdminRole.EDITOR):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
            
            # Get original questionnaire
            result = await db.execute(select(Questionnaire).where(Questionnaire.id == id))
            original = result.scalar_one_or_none()
            
            if not original:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Questionnaire not found")
            
            # Create cloned questionnaire
            cloned = Questionnaire(
                category_code=original.category_code,
                title=f"{original.title} (Copy)",
                description=original.description,
                status=QuestionnaireStatus.DRAFT
            )
            db.add(cloned)
            await db.commit()
            await db.refresh(cloned)
            
            # Clone questions
            questions_result = await db.execute(select(Question).where(Question.questionnaire_id == original.id))
            original_questions = questions_result.scalars().all()
            
            for original_question in original_questions:
                new_question = Question(
                    questionnaire_id=cloned.id,
                    key=original_question.key,
                    type=original_question.type,
                    label=original_question.label,
                    help_text=original_question.help_text,
                    required=original_question.required,
                    order_index=original_question.order_index,
                    constraints=original_question.constraints,
                    meta=original_question.meta
                )
                db.add(new_question)
                await db.commit()
                await db.refresh(new_question)
                
                # Clone options
                options_result = await db.execute(select(QuestionOption).where(QuestionOption.question_id == original_question.id))
                original_options = options_result.scalars().all()
                
                for original_option in original_options:
                    new_option = QuestionOption(
                        question_id=new_question.id,
                        value=original_option.value,
                        label=original_option.label,
                        order_index=original_option.order_index,
                        is_other=original_option.is_other
                    )
                    db.add(new_option)
                await db.commit()
            
            return QuestionnaireType(
                id=str(cloned.id),
                category_code=cloned.category_code,
                title=cloned.title,
                description=cloned.description,
                status=QuestionnaireStatusEnum(cloned.status.value),
                is_active=cloned.is_active,
                version=cloned.version,
                created_at=cloned.created_at,
                updated_at=cloned.updated_at,
                published_at=cloned.published_at,
                deleted_at=cloned.deleted_at,
                questions=[]
            )

    # Question Management Mutations
    @strawberry.mutation
    async def add_question(self, questionnaire_id: str, input: QuestionInput, info) -> Optional[QuestionTypeGraphQL]:
        """Add a question to an existing questionnaire (editor+)"""
        token = info.context.get("token")
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No token provided")
            
        payload = verify_token(token)
        admin_id = payload.get("sub")
        
        async for db in get_db():
            result = await db.execute(select(AdminUser).where(AdminUser.id == admin_id))
            admin_user = result.scalar_one_or_none()
            
            if not admin_user:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
            
            if not check_role_permission(admin_user.role, AdminRole.EDITOR):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
            
            # Get questionnaire
            result = await db.execute(select(Questionnaire).where(Questionnaire.id == questionnaire_id))
            questionnaire = result.scalar_one_or_none()
            
            if not questionnaire:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Questionnaire not found")
            
            if questionnaire.status != QuestionnaireStatus.DRAFT:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only draft questionnaires can be modified")
            
            # Create question
            question = Question(
                questionnaire_id=questionnaire.id,
                key=input.key,
                type=QuestionType(input.type.value),
                label=input.label,
                help_text=input.help_text,
                required=input.required,
                order_index=input.order_index,
                constraints=input.constraints,
                meta=input.meta
            )
            db.add(question)
            await db.commit()
            await db.refresh(question)
            
            # Create options if provided
            if input.options:
                for option_input in input.options:
                    option = QuestionOption(
                        question_id=question.id,
                        value=option_input.value,
                        label=option_input.label,
                        order_index=option_input.order_index,
                        is_other=option_input.is_other
                    )
                    db.add(option)
                await db.commit()
            
            return QuestionTypeGraphQL(
                id=str(question.id),
                questionnaire_id=str(question.questionnaire_id),
                key=question.key,
                type=QuestionTypeEnum(question.type.value),
                label=question.label,
                help_text=question.help_text,
                required=question.required,
                order_index=question.order_index,
                constraints=question.constraints,
                meta=question.meta,
                options=[]
            )

    @strawberry.mutation
    async def update_question(self, id: str, input: QuestionInput, info) -> Optional[QuestionTypeGraphQL]:
        """Update an existing question (editor+)"""
        token = info.context.get("token")
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No token provided")
            
        payload = verify_token(token)
        admin_id = payload.get("sub")
        
        async for db in get_db():
            result = await db.execute(select(AdminUser).where(AdminUser.id == admin_id))
            admin_user = result.scalar_one_or_none()
            
            if not admin_user:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
            
            if not check_role_permission(admin_user.role, AdminRole.EDITOR):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
            
            # Get question
            result = await db.execute(select(Question).where(Question.id == id))
            question = result.scalar_one_or_none()
            
            if not question:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
            
            # Check if questionnaire is draft
            questionnaire_result = await db.execute(select(Questionnaire).where(Questionnaire.id == question.questionnaire_id))
            questionnaire = questionnaire_result.scalar_one_or_none()
            
            if not questionnaire or questionnaire.status != QuestionnaireStatus.DRAFT:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only draft questionnaires can be modified")
            
            # Update question
            question.key = input.key
            question.type = QuestionType(input.type.value)
            question.label = input.label
            question.help_text = input.help_text
            question.required = input.required
            question.order_index = input.order_index
            question.constraints = input.constraints
            question.meta = input.meta
            
            # Update options if provided
            if input.options is not None:
                # Delete existing options
                existing_options_result = await db.execute(select(QuestionOption).where(QuestionOption.question_id == question.id))
                existing_options = existing_options_result.scalars().all()
                for option in existing_options:
                    await db.delete(option)
                
                # Add new options
                for option_input in input.options:
                    option = QuestionOption(
                        question_id=question.id,
                        value=option_input.value,
                        label=option_input.label,
                        order_index=option_input.order_index,
                        is_other=option_input.is_other
                    )
                    db.add(option)
            
            await db.commit()
            await db.refresh(question)
            
            return QuestionTypeGraphQL(
                id=str(question.id),
                questionnaire_id=str(question.questionnaire_id),
                key=question.key,
                type=QuestionTypeEnum(question.type.value),
                label=question.label,
                help_text=question.help_text,
                required=question.required,
                order_index=question.order_index,
                constraints=question.constraints,
                meta=question.meta,
                options=[]
            )

    @strawberry.mutation
    async def remove_question(self, id: str, info) -> bool:
        """Remove a question from questionnaire (editor+)"""
        token = info.context.get("token")
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No token provided")
            
        payload = verify_token(token)
        admin_id = payload.get("sub")
        
        async for db in get_db():
            result = await db.execute(select(AdminUser).where(AdminUser.id == admin_id))
            admin_user = result.scalar_one_or_none()
            
            if not admin_user:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
            
            if not check_role_permission(admin_user.role, AdminRole.EDITOR):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
            
            # Get question
            result = await db.execute(select(Question).where(Question.id == id))
            question = result.scalar_one_or_none()
            
            if not question:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
            
            # Check if questionnaire is draft
            questionnaire_result = await db.execute(select(Questionnaire).where(Questionnaire.id == question.questionnaire_id))
            questionnaire = questionnaire_result.scalar_one_or_none()
            
            if not questionnaire or questionnaire.status != QuestionnaireStatus.DRAFT:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only draft questionnaires can be modified")
            
            # Delete question (options will be deleted by cascade)
            await db.delete(question)
            await db.commit()
            
            return True

    @strawberry.mutation
    async def reorder_questions(self, questionnaire_id: str, orders: List[QuestionOrderInput], info) -> bool:
        """Reorder questions in a questionnaire (editor+)"""
        token = info.context.get("token")
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No token provided")
            
        payload = verify_token(token)
        admin_id = payload.get("sub")
        
        async for db in get_db():
            result = await db.execute(select(AdminUser).where(AdminUser.id == admin_id))
            admin_user = result.scalar_one_or_none()
            
            if not admin_user:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
            
            if not check_role_permission(admin_user.role, AdminRole.EDITOR):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
            
            # Get questionnaire
            result = await db.execute(select(Questionnaire).where(Questionnaire.id == questionnaire_id))
            questionnaire = result.scalar_one_or_none()
            
            if not questionnaire:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Questionnaire not found")
            
            if questionnaire.status != QuestionnaireStatus.DRAFT:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only draft questionnaires can be modified")
            
            # Update question order indices
            for order in orders:
                result = await db.execute(select(Question).where(Question.id == order.id))
                question = result.scalar_one_or_none()
                if question:
                    question.order_index = order.order_index
            
            await db.commit()
            return True

    # Option Management Mutations
    @strawberry.mutation
    async def add_option(self, question_id: str, input: QuestionOptionInput, info) -> Optional[QuestionOptionType]:
        """Add an option to a question (editor+)"""
        token = info.context.get("token")
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No token provided")
            
        payload = verify_token(token)
        admin_id = payload.get("sub")
        
        async for db in get_db():
            result = await db.execute(select(AdminUser).where(AdminUser.id == admin_id))
            admin_user = result.scalar_one_or_none()
            
            if not admin_user:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
            
            if not check_role_permission(admin_user.role, AdminRole.EDITOR):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
            
            # Get question
            result = await db.execute(select(Question).where(Question.id == question_id))
            question = result.scalar_one_or_none()
            
            if not question:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
            
            # Check if questionnaire is draft
            questionnaire_result = await db.execute(select(Questionnaire).where(Questionnaire.id == question.questionnaire_id))
            questionnaire = questionnaire_result.scalar_one_or_none()
            
            if not questionnaire or questionnaire.status != QuestionnaireStatus.DRAFT:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only draft questionnaires can be modified")
            
            # Create option
            option = QuestionOption(
                question_id=question.id,
                value=input.value,
                label=input.label,
                order_index=input.order_index,
                is_other=input.is_other
            )
            db.add(option)
            await db.commit()
            await db.refresh(option)
            
            return QuestionOptionType(
                id=str(option.id),
                question_id=str(option.question_id),
                value=option.value,
                label=option.label,
                order_index=option.order_index,
                is_other=option.is_other
            )

    @strawberry.mutation
    async def update_option(self, id: str, input: QuestionOptionInput, info) -> Optional[QuestionOptionType]:
        """Update an existing option (editor+)"""
        token = info.context.get("token")
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No token provided")
            
        payload = verify_token(token)
        admin_id = payload.get("sub")
        
        async for db in get_db():
            result = await db.execute(select(AdminUser).where(AdminUser.id == admin_id))
            admin_user = result.scalar_one_or_none()
            
            if not admin_user:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
            
            if not check_role_permission(admin_user.role, AdminRole.EDITOR):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
            
            # Get option
            result = await db.execute(select(QuestionOption).where(QuestionOption.id == id))
            option = result.scalar_one_or_none()
            
            if not option:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Option not found")
            
            # Check if questionnaire is draft
            question_result = await db.execute(select(Question).where(Question.id == option.question_id))
            question = question_result.scalar_one_or_none()
            
            if not question:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
            
            questionnaire_result = await db.execute(select(Questionnaire).where(Questionnaire.id == question.questionnaire_id))
            questionnaire = questionnaire_result.scalar_one_or_none()
            
            if not questionnaire or questionnaire.status != QuestionnaireStatus.DRAFT:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only draft questionnaires can be modified")
            
            # Update option
            option.value = input.value
            option.label = input.label
            option.order_index = input.order_index
            option.is_other = input.is_other
            
            await db.commit()
            await db.refresh(option)
            
            return QuestionOptionType(
                id=str(option.id),
                question_id=str(option.question_id),
                value=option.value,
                label=option.label,
                order_index=option.order_index,
                is_other=option.is_other
            )

    @strawberry.mutation
    async def remove_option(self, id: str, info) -> bool:
        """Remove an option from a question (editor+)"""
        token = info.context.get("token")
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No token provided")
            
        payload = verify_token(token)
        admin_id = payload.get("sub")
        
        async for db in get_db():
            result = await db.execute(select(AdminUser).where(AdminUser.id == admin_id))
            admin_user = result.scalar_one_or_none()
            
            if not admin_user:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
            
            if not check_role_permission(admin_user.role, AdminRole.EDITOR):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
            
            # Get option
            result = await db.execute(select(QuestionOption).where(QuestionOption.id == id))
            option = result.scalar_one_or_none()
            
            if not option:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Option not found")
            
            # Check if questionnaire is draft
            question_result = await db.execute(select(Question).where(Question.id == option.question_id))
            question = question_result.scalar_one_or_none()
            
            if not question:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
            
            questionnaire_result = await db.execute(select(Questionnaire).where(Questionnaire.id == question.questionnaire_id))
            questionnaire = questionnaire_result.scalar_one_or_none()
            
            if not questionnaire or questionnaire.status != QuestionnaireStatus.DRAFT:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only draft questionnaires can be modified")
            
            # Delete option
            await db.delete(option)
            await db.commit()
            
            return True

    # Enquiry Mutations
    @strawberry.mutation
    async def create_enquiry(self, input: EnquiryInput, info) -> EnquiryType:
        """Create a new enquiry (public, no auth required)"""
        # Extract IP and User-Agent from request context
        request = info.context.get("request")
        ip_address = None
        user_agent = None
        if request:
            ip_address = request.client.host if hasattr(request, 'client') else None
            user_agent = request.headers.get("user-agent")
        
        async for db in get_db():
            enquiry = Enquiry(
                venue_type=input.venue_type,
                venue_style=input.venue_style,
                product_category=input.product_category,
                child_category=input.child_category,
                legal_entity_name=input.legal_entity_name,
                trading_name=input.trading_name,
                entity_type=input.entity_type,
                abn=input.abn,
                acn=input.acn,
                liquor_license_number=input.liquor_license_number,
                outlet_type=input.outlet_type,
                business_address=input.business_address,
                business_city=input.business_city,
                business_state=input.business_state,
                business_postal_code=input.business_postal_code,
                first_name=input.first_name,
                surname=input.surname,
                contact_number=input.contact_number,
                email=input.email,
                unit_number=input.unit_number,
                street_number=input.street_number,
                street_name=input.street_name,
                referral_sourced=input.referral_sourced,
                cuisine=input.cuisine,
                outlet_style=input.outlet_style,
                apply_commercial_credit_terms=input.apply_commercial_credit_terms,
                application_id=input.application_id,
                ip_address=ip_address,
                user_agent=user_agent
            )
            db.add(enquiry)
            await db.commit()
            await db.refresh(enquiry)
            
            return EnquiryType(
                id=str(enquiry.id),
                status=EnquiryStatusGraphQL(enquiry.status.value),
                venue_type=enquiry.venue_type,
                venue_style=enquiry.venue_style,
                product_category=enquiry.product_category,
                child_category=enquiry.child_category,
                legal_entity_name=enquiry.legal_entity_name,
                trading_name=enquiry.trading_name,
                entity_type=enquiry.entity_type,
                abn=enquiry.abn,
                acn=enquiry.acn,
                liquor_license_number=enquiry.liquor_license_number,
                outlet_type=enquiry.outlet_type,
                business_address=enquiry.business_address,
                business_city=enquiry.business_city,
                business_state=enquiry.business_state,
                business_postal_code=enquiry.business_postal_code,
                first_name=enquiry.first_name,
                surname=enquiry.surname,
                contact_number=enquiry.contact_number,
                email=enquiry.email,
                unit_number=enquiry.unit_number,
                street_number=enquiry.street_number,
                street_name=enquiry.street_name,
                referral_sourced=enquiry.referral_sourced,
                cuisine=enquiry.cuisine,
                outlet_style=enquiry.outlet_style,
                apply_commercial_credit_terms=enquiry.apply_commercial_credit_terms,
                application_id=enquiry.application_id,
                questionnaire_id=str(enquiry.questionnaire_id) if enquiry.questionnaire_id else None,
                questionnaire_version=enquiry.questionnaire_version,
                questionnaire_title=enquiry.questionnaire_title,
                answers_json=enquiry.answers_json,
                submitted_at=enquiry.submitted_at,
                created_at=enquiry.created_at,
                updated_at=enquiry.updated_at,
                ip_address=enquiry.ip_address,
                user_agent=enquiry.user_agent,
                deleted_at=enquiry.deleted_at
            )

    @strawberry.mutation
    async def update_enquiry(self, id: str, input: EnquiryUpdateInput, info) -> Optional[EnquiryType]:
        """Update an enquiry"""
        async for db in get_db():
            result = await db.execute(select(Enquiry).where(Enquiry.id == id, Enquiry.deleted_at.is_(None)))
            enquiry = result.scalar_one_or_none()
            
            if not enquiry:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enquiry not found")
            
            if enquiry.status != EnquiryStatus.PENDING:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only pending enquiries can be updated")
            
            # Update fields if provided
            if input.venue_type is not None:
                enquiry.venue_type = input.venue_type
            if input.venue_style is not None:
                enquiry.venue_style = input.venue_style
            if input.product_category is not None:
                enquiry.product_category = input.product_category
            if input.child_category is not None:
                enquiry.child_category = input.child_category
            if input.legal_entity_name is not None:
                enquiry.legal_entity_name = input.legal_entity_name
            if input.trading_name is not None:
                enquiry.trading_name = input.trading_name
            if input.entity_type is not None:
                enquiry.entity_type = input.entity_type
            if input.abn is not None:
                enquiry.abn = input.abn
            if input.acn is not None:
                enquiry.acn = input.acn
            if input.liquor_license_number is not None:
                enquiry.liquor_license_number = input.liquor_license_number
            if input.outlet_type is not None:
                enquiry.outlet_type = input.outlet_type
            if input.business_address is not None:
                enquiry.business_address = input.business_address
            if input.business_city is not None:
                enquiry.business_city = input.business_city
            if input.business_state is not None:
                enquiry.business_state = input.business_state
            if input.business_postal_code is not None:
                enquiry.business_postal_code = input.business_postal_code
            if input.first_name is not None:
                enquiry.first_name = input.first_name
            if input.surname is not None:
                enquiry.surname = input.surname
            if input.contact_number is not None:
                enquiry.contact_number = input.contact_number
            if input.email is not None:
                enquiry.email = input.email
            if input.unit_number is not None:
                enquiry.unit_number = input.unit_number
            if input.street_number is not None:
                enquiry.street_number = input.street_number
            if input.street_name is not None:
                enquiry.street_name = input.street_name
            if input.referral_sourced is not None:
                enquiry.referral_sourced = input.referral_sourced
            if input.cuisine is not None:
                enquiry.cuisine = input.cuisine
            if input.outlet_style is not None:
                enquiry.outlet_style = input.outlet_style
            if input.apply_commercial_credit_terms is not None:
                enquiry.apply_commercial_credit_terms = input.apply_commercial_credit_terms
            if input.application_id is not None:
                enquiry.application_id = input.application_id
            
            await db.commit()
            await db.refresh(enquiry)
            
            return EnquiryType(
                id=str(enquiry.id),
                status=EnquiryStatusGraphQL(enquiry.status.value),
                venue_type=enquiry.venue_type,
                venue_style=enquiry.venue_style,
                product_category=enquiry.product_category,
                child_category=enquiry.child_category,
                legal_entity_name=enquiry.legal_entity_name,
                trading_name=enquiry.trading_name,
                entity_type=enquiry.entity_type,
                abn=enquiry.abn,
                acn=enquiry.acn,
                liquor_license_number=enquiry.liquor_license_number,
                outlet_type=enquiry.outlet_type,
                business_address=enquiry.business_address,
                business_city=enquiry.business_city,
                business_state=enquiry.business_state,
                business_postal_code=enquiry.business_postal_code,
                first_name=enquiry.first_name,
                surname=enquiry.surname,
                contact_number=enquiry.contact_number,
                email=enquiry.email,
                unit_number=enquiry.unit_number,
                street_number=enquiry.street_number,
                street_name=enquiry.street_name,
                referral_sourced=enquiry.referral_sourced,
                cuisine=enquiry.cuisine,
                outlet_style=enquiry.outlet_style,
                apply_commercial_credit_terms=enquiry.apply_commercial_credit_terms,
                application_id=enquiry.application_id,
                questionnaire_id=str(enquiry.questionnaire_id) if enquiry.questionnaire_id else None,
                questionnaire_version=enquiry.questionnaire_version,
                questionnaire_title=enquiry.questionnaire_title,
                answers_json=enquiry.answers_json,
                submitted_at=enquiry.submitted_at,
                created_at=enquiry.created_at,
                updated_at=enquiry.updated_at,
                ip_address=enquiry.ip_address,
                user_agent=enquiry.user_agent,
                deleted_at=enquiry.deleted_at
            )

    @strawberry.mutation
    async def submit_enquiry(self, id: str, questionnaire_id: str, questionnaire_version: int, questionnaire_title: str, answers: strawberry.scalars.JSON, info) -> Optional[EnquiryType]:
        """Submit an enquiry with questionnaire answers"""
        async for db in get_db():
            result = await db.execute(select(Enquiry).where(Enquiry.id == id, Enquiry.deleted_at.is_(None)))
            enquiry = result.scalar_one_or_none()
            
            if not enquiry:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enquiry not found")
            
            if enquiry.status != EnquiryStatus.PENDING:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only pending enquiries can be submitted")
            
            # Update enquiry with questionnaire data
            enquiry.status = EnquiryStatus.SUBMITTED
            enquiry.questionnaire_id = questionnaire_id
            enquiry.questionnaire_version = questionnaire_version
            enquiry.questionnaire_title = questionnaire_title
            enquiry.answers_json = answers
            enquiry.submitted_at = datetime.utcnow()
            
            # Generate and store Salesforce payload
            salesforce_payload = {
                "recordType": "Lead",
                "source": "OnboardingWizard",
                "venue": {
                    "venue_type": enquiry.venue_type,
                    "venue_style": enquiry.venue_style,
                    "outlet_type": enquiry.outlet_type,
                    "outlet_style": enquiry.outlet_style,
                    "cuisine": enquiry.cuisine,
                    "referral_sourced": enquiry.referral_sourced
                },
                "product_category": enquiry.product_category,
                "child_category": enquiry.child_category,
                "company": {
                    "legal_entity_name": enquiry.legal_entity_name,
                    "trading_name": enquiry.trading_name,
                    "entity_type": enquiry.entity_type,
                    "abn": enquiry.abn,
                    "acn": enquiry.acn,
                    "liquor_license_number": enquiry.liquor_license_number
                },
                "contact": {
                    "first_name": enquiry.first_name,
                    "surname": enquiry.surname,
                    "email": enquiry.email,
                    "contact_number": enquiry.contact_number
                },
                "address": {
                    "unit_number": enquiry.unit_number,
                    "street_number": enquiry.street_number,
                    "street_name": enquiry.street_name,
                    "business_city": enquiry.business_city,
                    "business_state": enquiry.business_state,
                    "business_postal_code": enquiry.business_postal_code
                },
                "questionnaire": {
                    "id": questionnaire_id,
                    "version": questionnaire_version,
                    "title": questionnaire_title
                },
                "answers": answers,
                "application": {
                    "apply_commercial_credit_terms": enquiry.apply_commercial_credit_terms,
                    "application_id": enquiry.application_id
                },
                "timestamps": {
                    "submitted_at": enquiry.submitted_at.isoformat()
                }
            }
            
            enquiry.salesforce_payload_json = salesforce_payload
            
            await db.commit()
            await db.refresh(enquiry)
            
            return EnquiryType(
                id=str(enquiry.id),
                status=EnquiryStatusGraphQL(enquiry.status.value),
                venue_type=enquiry.venue_type,
                venue_style=enquiry.venue_style,
                product_category=enquiry.product_category,
                child_category=enquiry.child_category,
                legal_entity_name=enquiry.legal_entity_name,
                trading_name=enquiry.trading_name,
                entity_type=enquiry.entity_type,
                abn=enquiry.abn,
                acn=enquiry.acn,
                liquor_license_number=enquiry.liquor_license_number,
                outlet_type=enquiry.outlet_type,
                business_address=enquiry.business_address,
                business_city=enquiry.business_city,
                business_state=enquiry.business_state,
                business_postal_code=enquiry.business_postal_code,
                first_name=enquiry.first_name,
                surname=enquiry.surname,
                contact_number=enquiry.contact_number,
                email=enquiry.email,
                unit_number=enquiry.unit_number,
                street_number=enquiry.street_number,
                street_name=enquiry.street_name,
                referral_sourced=enquiry.referral_sourced,
                cuisine=enquiry.cuisine,
                outlet_style=enquiry.outlet_style,
                apply_commercial_credit_terms=enquiry.apply_commercial_credit_terms,
                application_id=enquiry.application_id,
                questionnaire_id=str(enquiry.questionnaire_id) if enquiry.questionnaire_id else None,
                questionnaire_version=enquiry.questionnaire_version,
                questionnaire_title=enquiry.questionnaire_title,
                answers_json=enquiry.answers_json,
                submitted_at=enquiry.submitted_at,
                created_at=enquiry.created_at,
                updated_at=enquiry.updated_at,
                ip_address=enquiry.ip_address,
                user_agent=enquiry.user_agent,
                deleted_at=enquiry.deleted_at
            )
