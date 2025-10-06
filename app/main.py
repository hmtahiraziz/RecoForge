from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from typing import List, Optional
import boto3
from botocore.exceptions import ClientError
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db, Base, async_engine
from models import User, Post
from schemas import UserCreate, User as UserSchema, PostCreate, Post as PostSchema
from strawberry.fastapi import GraphQLRouter
from graphql_schema import schema
from recs.router import router as recs_router

app = FastAPI(
    title="My App API",
    description="FastAPI backend with REST and GraphQL APIs",
    version="1.0.0"
)

# GraphQL context function to extract JWT token from headers
async def get_context(request: Request):
    authorization = request.headers.get("Authorization")
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
    return {"request": request, "token": token}

# Add GraphQL router with playground and context
graphql_app = GraphQLRouter(schema, graphiql=True, context_getter=get_context)
app.include_router(graphql_app, prefix="/graphql")

# Add recommendations router
app.include_router(recs_router)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class HealthResponse(BaseModel):
    status: str
    timestamp: str

class HelloResponse(BaseModel):
    message: str

class FileInfo(BaseModel):
    name: str
    size: Optional[int] = None
    last_modified: Optional[str] = None

# Initialize S3 client (will use instance role)
s3_client = None
try:
    s3_client = boto3.client('s3', region_name=os.getenv('AWS_REGION', 'us-east-1'))
except Exception as e:
    print(f"S3 client initialization failed: {e}")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    from datetime import datetime
    return HealthResponse(
        status="OK",
        timestamp=datetime.utcnow().isoformat()
    )

@app.get("/api/hello", response_model=HelloResponse)
async def hello():
    """Simple hello endpoint"""
    return HelloResponse(message="Hello from FastAPI!")

@app.get("/api/files", response_model=List[FileInfo])
async def list_files():
    """List files from S3 bucket"""
    bucket_name = os.getenv('FILES_BUCKET')

    if not bucket_name:
        return [FileInfo(name="S3 bucket not configured")]

    if not s3_client:
        raise HTTPException(status_code=500, detail="S3 client not available")

    try:
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
        raise HTTPException(status_code=500, detail=f"S3 error: {str(e)}")

@app.post("/api/files/upload")
async def upload_file():
    """Upload file endpoint (placeholder)"""
    return {"message": "File upload endpoint - implement as needed"}

# Database endpoints
@app.post("/api/users/", response_model=UserSchema)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """Create a new user"""
    db_user = User(**user.dict())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@app.get("/api/users/", response_model=List[UserSchema])
async def get_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Get all users"""
    from sqlalchemy import select
    result = await db.execute(select(User).offset(skip).limit(limit))
    users = result.scalars().all()
    return users

@app.get("/api/users/{user_id}", response_model=UserSchema)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific user"""
    from sqlalchemy import select
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/api/posts/", response_model=PostSchema)
async def create_post(post: PostCreate, db: AsyncSession = Depends(get_db)):
    """Create a new post"""
    db_post = Post(**post.dict())
    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)
    return db_post

@app.get("/api/posts/", response_model=List[PostSchema])
async def get_posts(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Get all posts"""
    from sqlalchemy import select
    result = await db.execute(select(Post).offset(skip).limit(limit))
    posts = result.scalars().all()
    return posts

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
