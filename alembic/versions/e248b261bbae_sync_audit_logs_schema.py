"""sync audit_logs schema

Revision ID: e248b261bbae
Revises: cde3ccd95e52
Create Date: 2026-02-04 16:43:13.627543

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e248b261bbae'
down_revision: Union[str, Sequence[str], None] = 'cde3ccd95e52'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass

def downgrade() -> None:
    pass