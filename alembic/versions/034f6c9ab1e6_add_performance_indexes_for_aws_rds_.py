"""Add performance indexes for AWS RDS optimization

Revision ID: 034f6c9ab1e6
Revises: c38c43c79949
Create Date: 2025-10-28 22:14:41.558702

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '034f6c9ab1e6'
down_revision: Union[str, Sequence[str], None] = 'c38c43c79949'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add performance indexes for AWS RDS optimization."""
    
    # Composite indexes for common query patterns
    
    # Shopping lists - frequently queried by kitchen and creation date
    op.create_index(
        'idx_shopping_lists_kitchen_created', 
        'shopping_lists', 
        ['kitchen_id', 'created_at']
    )
    
    # Shopping list items - frequently queried by list and purchase status
    op.create_index(
        'idx_shopping_list_items_list_purchased', 
        'shopping_list_items', 
        ['shopping_list_id', 'is_purchased']
    )
    
    # Shopping list items - category filtering
    op.create_index(
        'idx_shopping_list_items_category', 
        'shopping_list_items', 
        ['category']
    )
    
    # Pantry items - kitchen and name for search
    op.create_index(
        'idx_pantry_items_kitchen_name', 
        'pantry_items', 
        ['kitchen_id', 'name']
    )
    
    # Pantry items - UPC lookup
    op.create_index(
        'idx_pantry_items_upc', 
        'pantry_items', 
        ['upc']
    )
    
    # Refrigerator items - kitchen and name for search
    op.create_index(
        'idx_refrigerator_items_kitchen_name', 
        'refrigerator_items', 
        ['kitchen_id', 'name']
    )
    
    # Refrigerator items - UPC lookup
    op.create_index(
        'idx_refrigerator_items_upc', 
        'refrigerator_items', 
        ['upc']
    )
    
    # Freezer items - kitchen and name for search
    op.create_index(
        'idx_freezer_items_kitchen_name', 
        'freezer_items', 
        ['kitchen_id', 'name']
    )
    
    # Freezer items - UPC lookup
    op.create_index(
        'idx_freezer_items_upc', 
        'freezer_items', 
        ['upc']
    )
    
    # Users - email lookup (if not already indexed)
    op.create_index(
        'idx_users_email_active', 
        'users', 
        ['email', 'is_active']
    )
    
    # Kitchens - owner lookup with creation date for sorting
    op.create_index(
        'idx_kitchens_owner_created', 
        'kitchens', 
        ['owner_id', 'created_at']
    )
    
    # Full-text search indexes for PostgreSQL
    # These use PostgreSQL's GIN indexes for better text search performance
    
    # Shopping list items - full text search on name and description
    op.execute("""
        CREATE INDEX idx_shopping_list_items_fulltext 
        ON shopping_list_items 
        USING gin(to_tsvector('english', coalesce(name, '') || ' ' || coalesce(description, '') || ' ' || coalesce(notes, '')))
    """)
    
    # Pantry items - full text search
    op.execute("""
        CREATE INDEX idx_pantry_items_fulltext 
        ON pantry_items 
        USING gin(to_tsvector('english', coalesce(name, '') || ' ' || coalesce(description, '')))
    """)
    
    # Refrigerator items - full text search
    op.execute("""
        CREATE INDEX idx_refrigerator_items_fulltext 
        ON refrigerator_items 
        USING gin(to_tsvector('english', coalesce(name, '') || ' ' || coalesce(description, '')))
    """)
    
    # Freezer items - full text search
    op.execute("""
        CREATE INDEX idx_freezer_items_fulltext 
        ON freezer_items 
        USING gin(to_tsvector('english', coalesce(name, '') || ' ' || coalesce(description, '')))
    """)
    
    # Partial indexes for active records (PostgreSQL optimization)
    op.create_index(
        'idx_users_active_username', 
        'users', 
        ['username'], 
        postgresql_where=sa.text('is_active = true')
    )


def downgrade() -> None:
    """Downgrade schema - Remove performance indexes."""
    
    # Drop composite indexes
    op.drop_index('idx_shopping_lists_kitchen_created', table_name='shopping_lists')
    op.drop_index('idx_shopping_list_items_list_purchased', table_name='shopping_list_items')
    op.drop_index('idx_shopping_list_items_category', table_name='shopping_list_items')
    
    op.drop_index('idx_pantry_items_kitchen_name', table_name='pantry_items')
    op.drop_index('idx_pantry_items_upc', table_name='pantry_items')
    
    op.drop_index('idx_refrigerator_items_kitchen_name', table_name='refrigerator_items')
    op.drop_index('idx_refrigerator_items_upc', table_name='refrigerator_items')
    
    op.drop_index('idx_freezer_items_kitchen_name', table_name='freezer_items')
    op.drop_index('idx_freezer_items_upc', table_name='freezer_items')
    
    op.drop_index('idx_users_email_active', table_name='users')
    op.drop_index('idx_kitchens_owner_created', table_name='kitchens')
    
    # Drop full-text search indexes
    op.drop_index('idx_shopping_list_items_fulltext', table_name='shopping_list_items')
    op.drop_index('idx_pantry_items_fulltext', table_name='pantry_items')
    op.drop_index('idx_refrigerator_items_fulltext', table_name='refrigerator_items')
    op.drop_index('idx_freezer_items_fulltext', table_name='freezer_items')
    
    # Drop partial indexes
    op.drop_index('idx_users_active_username', table_name='users')
