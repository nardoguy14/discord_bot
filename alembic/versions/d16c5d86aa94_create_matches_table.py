"""create matches table

Revision ID: d16c5d86aa94
Revises: 471cfccda96b
Create Date: 2024-06-06 00:12:41.434283

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision: str = 'd16c5d86aa94'
down_revision: Union[str, None] = '471cfccda96b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'matches',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('player_id', sa.VARCHAR(256), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=func.now()),
        sa.Column('modified_at', sa.DateTime(), nullable=False, server_default=func.now())
    )


def downgrade() -> None:
    op.drop_table('matches')
