"""final_enquiry_schema_cleanup

Revision ID: 7d50eb03de54
Revises: be92b034908f
Create Date: 2025-09-16 18:27:42.255159

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7d50eb03de54'
down_revision = 'be92b034908f'
branch_labels = None
depends_on = None


def upgrade():
    # Drop the existing enquiries table and recreate with correct schema
    op.drop_table('enquiries')
    
    # Create the enquiries table with the final correct schema
    op.create_table('enquiries',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'SUBMITTED', name='enquirystatus', create_type=False), nullable=False),
        
        # Step 1-2 (venue + selection scope)
        sa.Column('venue_type', sa.String(), nullable=False),
        sa.Column('venue_style', sa.String(), nullable=True),
        sa.Column('product_category', sa.String(), nullable=False),
        sa.Column('child_category', sa.String(), nullable=True),
        
        # Profile / business fields
        sa.Column('legal_entity_name', sa.String(), nullable=True),
        sa.Column('trading_name', sa.String(), nullable=True),
        sa.Column('entity_type', sa.String(), nullable=True),
        sa.Column('abn', sa.String(), nullable=True),
        sa.Column('acn', sa.String(), nullable=True),
        sa.Column('liquor_license_number', sa.String(), nullable=True),
        sa.Column('outlet_type', sa.String(), nullable=True),
        sa.Column('business_address', sa.String(), nullable=True),
        sa.Column('business_city', sa.String(), nullable=True),
        sa.Column('business_state', sa.String(), nullable=True),
        sa.Column('business_postal_code', sa.String(), nullable=True),
        sa.Column('first_name', sa.String(), nullable=True),
        sa.Column('surname', sa.String(), nullable=True),
        sa.Column('contact_number', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('unit_number', sa.String(), nullable=True),
        sa.Column('street_number', sa.String(), nullable=True),
        sa.Column('street_name', sa.String(), nullable=True),
        sa.Column('referral_sourced', sa.String(), nullable=True),
        sa.Column('cuisine', sa.String(), nullable=True),
        sa.Column('outlet_style', sa.String(), nullable=True),
        sa.Column('apply_commercial_credit_terms', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('application_id', sa.Integer(), nullable=True),
        
        # Questionnaire snapshot + answers (set on submit)
        sa.Column('questionnaire_id', sa.UUID(), nullable=True),
        sa.Column('questionnaire_version', sa.Integer(), nullable=True),
        sa.Column('questionnaire_title', sa.String(), nullable=True),
        sa.Column('answers_json', sa.JSON(), nullable=True),
        
        # SF payload snapshot (store only, never expose in GraphQL)
        sa.Column('salesforce_payload_json', sa.JSON(), nullable=True),
        
        # Meta
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('user_agent', sa.String(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_enquiry_status', 'enquiries', ['status'], unique=False)
    op.create_index('idx_enquiry_venue_type', 'enquiries', ['venue_type'], unique=False)
    op.create_index('idx_enquiry_venue_style', 'enquiries', ['venue_style'], unique=False)
    op.create_index('idx_enquiry_email', 'enquiries', ['email'], unique=False)
    op.create_index('idx_enquiry_created_at', 'enquiries', ['created_at'], unique=False)
    op.create_index(op.f('ix_enquiries_id'), 'enquiries', ['id'], unique=False)
    
    # Add unique constraint on email
    op.create_unique_constraint('uq_enquiries_email', 'enquiries', ['email'])


def downgrade():
    # Drop the enquiries table
    op.drop_table('enquiries')
