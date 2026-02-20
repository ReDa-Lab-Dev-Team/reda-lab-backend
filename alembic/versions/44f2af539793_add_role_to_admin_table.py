""" Add role to admin table

Revision ID: 44f2af539793
Revises: f8c6ffbf9052
Create Date: 2026-02-20 14:41:35.371051

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '44f2af539793'
down_revision: Union[str, Sequence[str], None] = 'f8c6ffbf9052'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add column as nullable first
    op.add_column('admins', sa.Column('role', sa.String(length=20), nullable=True))
    
    # Set default value for existing rows
    op.execute("UPDATE admins SET role = 'admin' WHERE role IS NULL")
    
    # Now make it NOT NULL
    op.alter_column('admins', 'role', nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('admins', 'role')