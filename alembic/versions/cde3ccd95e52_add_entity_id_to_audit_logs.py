"""add entity_id to audit_logs

Revision ID: cde3ccd95e52
Revises: 889cbb588a10
Create Date: 2026-02-04 16:34:24.383249

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cde3ccd95e52'
down_revision: Union[str, Sequence[str], None] = '889cbb588a10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass

def downgrade() -> None:
    pass