"""Add admin_user table

Revision ID: 001_add_admin_user_table
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_add_admin_user_table'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create admin_role enum
    admin_role_enum = postgresql.ENUM('superadmin', 'editor', 'viewer', name='adminrole')
    admin_role_enum.create(op.get_bind())
    
    # Create admin_users table
    op.create_table('admin_users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('role', admin_role_enum, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admin_users_id'), 'admin_users', ['id'], unique=False)
    op.create_index(op.f('ix_admin_users_email'), 'admin_users', ['email'], unique=True)


def downgrade():
    # Drop admin_users table
    op.drop_index(op.f('ix_admin_users_email'), table_name='admin_users')
    op.drop_index(op.f('ix_admin_users_id'), table_name='admin_users')
    op.drop_table('admin_users')
    
    # Drop admin_role enum
    admin_role_enum = postgresql.ENUM('superadmin', 'editor', 'viewer', name='adminrole')
    admin_role_enum.drop(op.get_bind())
