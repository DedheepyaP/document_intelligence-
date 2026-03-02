"""drop role column from users

Revision ID: 003_drop_role_column
Revises: 002_add_role_table_direct
Create Date: 2026-02-18 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003_drop_role_column'
down_revision: Union[str, Sequence[str], None] = '002_add_role_table_direct'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop role column
    op.drop_column('users', 'role')


def downgrade() -> None:
    # Re-add likely role column type
    op.add_column('users', sa.Column('role', sa.String(length=50), nullable=True))
