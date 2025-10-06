#!/usr/bin/env python3
"""
Script to create the first superadmin user.
Run this after running the database migration.
"""

import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import AsyncSession
from database import AsyncSessionLocal, async_engine
from models import AdminUser, AdminRole, Base
from auth_utils import get_password_hash

async def create_superadmin():
    """Create the first superadmin user."""
    
    # Create tables if they don't exist
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as db:
        # Check if any superadmin already exists
        from sqlalchemy import select
        result = await db.execute(select(AdminUser).where(AdminUser.role == AdminRole.SUPERADMIN))
        existing_superadmin = result.scalar_one_or_none()
        
        if existing_superadmin:
            print(f"Superadmin already exists: {existing_superadmin.email}")
            return
        
        # Get email and password from environment or prompt
        email = os.getenv("SUPERADMIN_EMAIL", "admin@example.com")
        password = os.getenv("SUPERADMIN_PASSWORD", "admin123")
        
        print(f"Creating superadmin with email: {email}")
        
        # Create superadmin
        superadmin = AdminUser(
            email=email,
            password_hash=get_password_hash(password),
            role=AdminRole.SUPERADMIN
        )
        
        db.add(superadmin)
        await db.commit()
        await db.refresh(superadmin)
        
        print(f"Superadmin created successfully!")
        print(f"ID: {superadmin.id}")
        print(f"Email: {superadmin.email}")
        print(f"Role: {superadmin.role.value}")
        print(f"Created at: {superadmin.created_at}")

if __name__ == "__main__":
    asyncio.run(create_superadmin())
