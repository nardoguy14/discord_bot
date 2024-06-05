"""altering league user table add ranking column

Revision ID: 4887ed38348a
Revises: f6473d37761b
Create Date: 2024-06-04 10:31:22.580793

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4887ed38348a'
down_revision: Union[str, None] = 'f6473d37761b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('league_users', sa.Column('ranking', sa.DECIMAL, nullable=True))


def downgrade() -> None:
    op.drop_column('league_users', 'ranking')
