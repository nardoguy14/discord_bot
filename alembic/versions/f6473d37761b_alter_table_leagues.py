"""alter table leagues

Revision ID: f6473d37761b
Revises: 69955991ccbf
Create Date: 2024-05-31 22:50:00.332132

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f6473d37761b'
down_revision: Union[str, None] = '69955991ccbf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('leagues', sa.Column('max_plays_per_week', sa.Integer, nullable=True))
    op.add_column('leagues', sa.Column('rules', sa.Text, nullable=True))

def downgrade():
    op.drop_column('leagues', 'max_plays_per_week')
    op.drop_column('leagues', 'rules')
