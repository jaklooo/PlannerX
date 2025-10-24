"""create initial tables

Revision ID: 001
Revises: 
Create Date: 2025-10-22 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Create initial database schema."""
    # Users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uid', sa.String(length=128), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('email_verified', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('digest_enabled', sa.Boolean(), nullable=True),
        sa.Column('digest_time', sa.String(length=5), nullable=True),
        sa.Column('sms_enabled', sa.Boolean(), nullable=True),
        sa.Column('phone_number', sa.String(length=20), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_uid'), 'users', ['uid'], unique=True)
    
    # Projects table
    op.create_table('projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_projects_user_id'), 'projects', ['user_id'], unique=False)
    
    # Tasks table
    op.create_table('tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('due_at', sa.DateTime(), nullable=True),
        sa.Column('priority', sa.String(length=20), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tasks_user_id'), 'tasks', ['user_id'], unique=False)
    op.create_index(op.f('ix_tasks_due_at'), 'tasks', ['due_at'], unique=False)
    op.create_index(op.f('ix_tasks_status'), 'tasks', ['status'], unique=False)
    
    # Events table
    op.create_table('events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('start_at', sa.DateTime(), nullable=False),
        sa.Column('end_at', sa.DateTime(), nullable=True),
        sa.Column('repeat_rule', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_events_user_id'), 'events', ['user_id'], unique=False)
    op.create_index(op.f('ix_events_start_at'), 'events', ['start_at'], unique=False)
    
    # Contacts table
    op.create_table('contacts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('birthday_date', sa.Date(), nullable=True),
        sa.Column('name_day_date', sa.Date(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_contacts_user_id'), 'contacts', ['user_id'], unique=False)


def downgrade():
    """Drop all tables."""
    op.drop_index(op.f('ix_contacts_user_id'), table_name='contacts')
    op.drop_table('contacts')
    op.drop_index(op.f('ix_events_start_at'), table_name='events')
    op.drop_index(op.f('ix_events_user_id'), table_name='events')
    op.drop_table('events')
    op.drop_index(op.f('ix_tasks_status'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_due_at'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_user_id'), table_name='tasks')
    op.drop_table('tasks')
    op.drop_index(op.f('ix_projects_user_id'), table_name='projects')
    op.drop_table('projects')
    op.drop_index(op.f('ix_users_uid'), table_name='users')
    op.drop_table('users')
