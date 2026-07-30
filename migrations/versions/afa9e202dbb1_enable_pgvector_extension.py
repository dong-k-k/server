"""enable pgvector extension

Revision ID: afa9e202dbb1
Revises: 
Create Date: 2026-07-30 16:51:48.306557

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'afa9e202dbb1'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

def downgrade():
    op.execute("DROP EXTENSION IF EXISTS vector")
