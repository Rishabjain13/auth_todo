"""final sync audit and templates

Revision ID: b3da427f1aed
Revises: e248b261bbae
Create Date: 2026-02-04 16:54:33.924167

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3da427f1aed'
down_revision: Union[str, Sequence[str], None] = 'e248b261bbae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # entity_id already exists in DB – do NOT add again

    # ensure timestamp exists
    op.add_column(
        "audit_logs",
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False
        )
    )

    # create task_templates if not exists
    op.create_table(
        "task_templates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("priority", sa.String(), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
    )

def downgrade() -> None:
    # op.drop_table("task_templates")
    # op.drop_column("audit_logs", "timestamp")
    # op.drop_column("audit_logs", "entity_id")
    pass
