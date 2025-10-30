"""Add pantry, refrigerator, and freezer item tables

Revision ID: 42d9e070349b
Revises: 034f6c9ab1e6
Create Date: 2025-10-30 22:29:06.021753

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '42d9e070349b'
down_revision: Union[str, Sequence[str], None] = 'c38c43c79949'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create pantry_items table
    op.create_table(
        'pantry_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('quantity', sa.String(length=50), nullable=True),
        sa.Column('quantity_type', sa.String(length=50), nullable=True),
        sa.Column('upc', sa.String(length=20), nullable=True),
        sa.Column('kitchen_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['kitchen_id'], ['kitchens.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pantry_items_id'), 'pantry_items', ['id'], unique=False)

    # Create refrigerator_items table
    op.create_table(
        'refrigerator_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('quantity', sa.String(length=50), nullable=True),
        sa.Column('quantity_type', sa.String(length=50), nullable=True),
        sa.Column('upc', sa.String(length=20), nullable=True),
        sa.Column('kitchen_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['kitchen_id'], ['kitchens.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_refrigerator_items_id'), 'refrigerator_items', ['id'], unique=False)

    # Create freezer_items table
    op.create_table(
        'freezer_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('quantity', sa.String(length=50), nullable=True),
        sa.Column('quantity_type', sa.String(length=50), nullable=True),
        sa.Column('upc', sa.String(length=20), nullable=True),
        sa.Column('kitchen_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['kitchen_id'], ['kitchens.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_freezer_items_id'), 'freezer_items', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_freezer_items_id'), table_name='freezer_items')
    op.drop_table('freezer_items')
    op.drop_index(op.f('ix_refrigerator_items_id'), table_name='refrigerator_items')
    op.drop_table('refrigerator_items')
    op.drop_index(op.f('ix_pantry_items_id'), table_name='pantry_items')
    op.drop_table('pantry_items')
