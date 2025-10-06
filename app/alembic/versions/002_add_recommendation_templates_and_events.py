"""add_recommendation_templates_and_events

Revision ID: 002
Revises: def950ae90aa
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = 'def950ae90aa'
branch_labels = None
depends_on = None


def upgrade():
    # Create enum type for action
    action_type_enum = postgresql.ENUM('shown', 'clicked', 'added', 'purchased', name='actiontype')
    action_type_enum.create(op.get_bind())

    # Create recommendation_templates table
    op.create_table('recommendation_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('template_name', sa.String(), nullable=True),
        sa.Column('items', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recommendation_templates_id'), 'recommendation_templates', ['id'], unique=False)
    op.create_index(op.f('ix_recommendation_templates_user_id'), 'recommendation_templates', ['user_id'], unique=False)

    # Create recommendation_events table
    op.create_table('recommendation_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('sku', sa.String(), nullable=False),
        sa.Column('action', action_type_enum, nullable=False),
        sa.Column('meta', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['template_id'], ['recommendation_templates.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recommendation_events_id'), 'recommendation_events', ['id'], unique=False)
    op.create_index(op.f('ix_recommendation_events_user_id'), 'recommendation_events', ['user_id'], unique=False)
    op.create_index(op.f('ix_recommendation_events_sku'), 'recommendation_events', ['sku'], unique=False)


def downgrade():
    # Drop tables
    op.drop_index(op.f('ix_recommendation_events_sku'), table_name='recommendation_events')
    op.drop_index(op.f('ix_recommendation_events_user_id'), table_name='recommendation_events')
    op.drop_index(op.f('ix_recommendation_events_id'), table_name='recommendation_events')
    op.drop_table('recommendation_events')

    op.drop_index(op.f('ix_recommendation_templates_user_id'), table_name='recommendation_templates')
    op.drop_index(op.f('ix_recommendation_templates_id'), table_name='recommendation_templates')
    op.drop_table('recommendation_templates')

    # Drop enum type
    action_type_enum = postgresql.ENUM('shown', 'clicked', 'added', 'purchased', name='actiontype')
    action_type_enum.drop(op.get_bind())
