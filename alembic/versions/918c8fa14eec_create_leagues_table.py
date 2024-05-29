"""create leagues table

Revision ID: 918c8fa14eec
Revises: 
Create Date: 2024-05-28 17:00:18.633109

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision: str = '918c8fa14eec'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'leagues',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.VARCHAR(256), nullable=False),
        sa.Column('kind', sa.VARCHAR(256), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=func.now()),
        sa.Column('modified_at', sa.DateTime(), nullable=False, server_default=func.now())
    )


def downgrade() -> None:
    op.drop_table("leagues")
