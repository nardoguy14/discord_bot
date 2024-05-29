"""create user to league table

Revision ID: 947d17c757bc
Revises: 918c8fa14eec
Create Date: 2024-05-28 18:56:05.242675

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision: str = '947d17c757bc'
down_revision: Union[str, None] = '918c8fa14eec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'league_users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.VARCHAR(255), nullable=False),
        sa.Column('league_id', sa.Integer, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=func.now()),
        sa.Column('modified_at', sa.DateTime(), nullable=False, server_default=func.now())
    )


def downgrade() -> None:
    op.drop_table("league_users")
