"""remove_items_table

Revision ID: remove_items_table
Revises: create_superadmin
Create Date: 2023-06-15 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'remove_items_table'
down_revision: Union[str, None] = 'create_superadmin'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Eliminar la tabla items."""
    op.drop_index('ix_items_id', table_name='items')
    op.drop_table('items')


def downgrade() -> None:
    """Recrear la tabla items."""
    op.create_table('items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_items_id', 'items', ['id'], unique=False)
