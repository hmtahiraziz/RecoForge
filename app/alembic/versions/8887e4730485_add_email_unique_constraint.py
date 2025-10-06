"""add_email_unique_constraint

Revision ID: 8887e4730485
Revises: be92b034908f
Create Date: 2025-09-16 18:28:28.355748

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8887e4730485'
down_revision = 'be92b034908f'
branch_labels = None
depends_on = None


def upgrade():
    # Add unique constraint on email field
    op.create_unique_constraint('uq_enquiries_email', 'enquiries', ['email'])


def downgrade():
    # Remove unique constraint on email field
    op.drop_constraint('uq_enquiries_email', 'enquiries', type_='unique')
