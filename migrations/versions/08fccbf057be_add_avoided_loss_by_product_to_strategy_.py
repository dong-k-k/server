"""add avoided_loss_by_product to strategy_recommendation

Revision ID: 08fccbf057be
Revises: a1c9f0e2b7d4
Create Date: 2026-08-03 01:42:19.168395

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '08fccbf057be'
down_revision: Union[str, Sequence[str], None] = 'a1c9f0e2b7d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {c["name"] for c in inspector.get_columns("strategy_recommendation")}
    if "avoided_loss_by_product" not in columns:
        op.add_column(
            "strategy_recommendation",
            sa.Column("avoided_loss_by_product", sa.JSON(), nullable=True),
        )


def downgrade():
    pass
