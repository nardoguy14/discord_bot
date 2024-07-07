"""add column to user

Revision ID: ed27be6c1aeb
Revises: 074f4fd41096
Create Date: 2024-07-06 19:34:41.497136

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ed27be6c1aeb'
down_revision: Union[str, None] = '074f4fd41096'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('users', sa.Column('wallet_address', sa.Integer, nullable=True))

def downgrade():
    op.drop_column('users', 'wallet_address')
