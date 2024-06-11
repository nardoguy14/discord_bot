"""alter table matches add column ready up

Revision ID: afab5ac281e4
Revises: d16c5d86aa94
Create Date: 2024-06-10 00:42:50.083168

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'afab5ac281e4'
down_revision: Union[str, None] = 'd16c5d86aa94'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('matches', sa.Column('ready_up_1', sa.Boolean(), nullable=True))
    op.add_column('matches', sa.Column('ready_up_2', sa.Boolean(), nullable=True))


def downgrade() -> None:
    op.drop_column('matches', 'ready_up_1')
    op.drop_column('matches', 'ready_up_2')
