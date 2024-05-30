"""create role table

Revision ID: c5d59aafcf23
Revises: 947d17c757bc
Create Date: 2024-05-29 20:21:45.607630

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision: str = 'c5d59aafcf23'
down_revision: Union[str, None] = '947d17c757bc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.VARCHAR(256), nullable=False),
        sa.Column('role_id', sa.VARCHAR(256), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=func.now()),
        sa.Column('modified_at', sa.DateTime(), nullable=False, server_default=func.now())
    )


def downgrade() -> None:
    op.drop_table('roles')
