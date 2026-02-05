"""fix audit_logs columns

Revision ID: 889cbb588a10
Revises: d1750ae4a146
Create Date: 2026-02-04 16:14:23.490872

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '889cbb588a10'
down_revision: Union[str, Sequence[str], None] = 'd1750ae4a146'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass

def downgrade() -> None:
    pass