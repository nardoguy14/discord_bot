"""modify matches table create column deck code

Revision ID: 074f4fd41096
Revises: afab5ac281e4
Create Date: 2024-06-14 21:46:41.444663

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '074f4fd41096'
down_revision: Union[str, None] = 'afab5ac281e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("matches", sa.Column("deck_code_1", sa.String(), nullable=True))
    op.add_column("matches", sa.Column("deck_code_2", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("matches", "deck_code_1")
    op.drop_column("matches", "deck_code_2")
