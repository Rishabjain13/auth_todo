"""add user_id to audit_logs

Revision ID: d1750ae4a146
Revises: 88e5ba647445
Create Date: 2026-02-04 15:47:27.639324

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd1750ae4a146'
down_revision: Union[str, Sequence[str], None] = '88e5ba647445'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "audit_logs",
        sa.Column("user_id", sa.Integer(), nullable=True)
    )

    # 2. backfill (system / legacy logs)
    op.execute(
        "UPDATE audit_logs SET user_id = NULL WHERE user_id IS NULL"
    )

    # 3. add FK
    op.create_foreign_key(
        "fk_audit_logs_user_id",
        "audit_logs",
        "users",
        ["user_id"],
        ["id"]
    )


    
def downgrade() -> None:
    op.drop_constraint("fk_audit_logs_user_id", "audit_logs", type_="foreignkey")
    op.drop_column("audit_logs", "user_id")
   
