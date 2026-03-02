"""add role table with direct relationship

Revision ID: 002_add_role_table_direct
Revises: 8e928396981c
Create Date: 2026-02-18 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002_add_role_table_direct'
down_revision: Union[str, Sequence[str], None] = '8e928396981c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Create roles table and add role_id to users."""
    
    # Create roles table
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Add role_id to users table
    op.add_column('users', sa.Column('role_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_users_role_id', 'users', 'roles', ['role_id'], ['id'])
    
    # Seed initial roles
    op.execute("""
        INSERT INTO roles (name, description) VALUES
        ('admin', 'Administrator with full access'),
        ('doctor', 'Medical professional'),
        ('lawyer', 'Legal professional'),
        ('researcher', 'Research professional'),
        ('consultant', 'Business consultant'),
        ('analyst', 'Financial analyst'),
        ('general', 'General user')
    """)
    
    # Set all existing users to 'general' role
    op.execute("""
        UPDATE users 
        SET role_id = (SELECT id FROM roles WHERE name = 'general')
        WHERE role_id IS NULL
    """)
    
    # Make role_id NOT NULL
    op.alter_column('users', 'role_id', existing_type=sa.Integer(), nullable=False)


def downgrade() -> None:
    """Downgrade schema - Remove roles table and role_id from users."""
    
    # Drop foreign key and column
    op.drop_constraint('fk_users_role_id', 'users', type_='foreignkey')
    op.drop_column('users', 'role_id')
    
    # Drop roles table
    op.drop_table('roles')
