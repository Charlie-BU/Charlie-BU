"""empty message

Revision ID: 792b3312ad9c
Revises: 599dc70a717f
Create Date: 2025-06-27 22:48:47.522061

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '792b3312ad9c'
down_revision: Union[str, None] = '599dc70a717f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
