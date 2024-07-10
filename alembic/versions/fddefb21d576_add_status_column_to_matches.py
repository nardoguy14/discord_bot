"""add status column to matches

Revision ID: fddefb21d576
Revises: ed27be6c1aeb
Create Date: 2024-07-09 16:38:38.938476

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fddefb21d576'
down_revision: Union[str, None] = 'ed27be6c1aeb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('matches', sa.Column('status', sa.String, nullable=True))


def downgrade() -> None:
    op.drop_column('matches', 'status')
