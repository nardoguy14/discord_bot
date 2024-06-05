"""alter table league add max disparity

Revision ID: 471cfccda96b
Revises: 4887ed38348a
Create Date: 2024-06-04 16:42:33.069224

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '471cfccda96b'
down_revision: Union[str, None] = '4887ed38348a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("leagues", sa.Column("max_disparity", sa.DECIMAL, nullable=True))


def downgrade() -> None:
    op.drop_column("leagues", "max_disparity")
