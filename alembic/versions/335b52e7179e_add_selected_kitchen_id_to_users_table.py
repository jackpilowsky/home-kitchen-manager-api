"""Add selected_kitchen_id to users table

Revision ID: 335b52e7179e
Revises: 034f6c9ab1e6
Create Date: 2025-10-31 01:04:51.230824

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '335b52e7179e'
down_revision: Union[str, Sequence[str], None] = '034f6c9ab1e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add selected_kitchen_id column to users table
    op.add_column('users', sa.Column('selected_kitchen_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_users_selected_kitchen', 'users', 'kitchens', ['selected_kitchen_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_users_selected_kitchen', 'users', type_='foreignkey')
    op.drop_column('users', 'selected_kitchen_id')
