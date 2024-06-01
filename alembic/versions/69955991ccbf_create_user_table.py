"""create user table

Revision ID: 69955991ccbf
Revises: c5d59aafcf23
Create Date: 2024-05-30 00:16:41.250477

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision: str = '69955991ccbf'
down_revision: Union[str, None] = 'c5d59aafcf23'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('discord_id', sa.VARCHAR(256), nullable=False),
        sa.Column('gu_user_name', sa.VARCHAR(256), nullable=False),
        sa.Column('gu_user_id', sa.VARCHAR(256), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=func.now()),
        sa.Column('modified_at', sa.DateTime(), nullable=False, server_default=func.now())
    )


def downgrade() -> None:
    pass
