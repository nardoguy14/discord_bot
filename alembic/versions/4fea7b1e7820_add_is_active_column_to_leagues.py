"""add is_active column to leagues

Revision ID: 4fea7b1e7820
Revises: fddefb21d576
Create Date: 2024-08-17 17:49:30.983714

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4fea7b1e7820'
down_revision: Union[str, None] = 'fddefb21d576'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('leagues', sa.Column('is_active', sa.Boolean, default=False))

def downgrade():
    op.drop_column('leagues', 'is_active')
