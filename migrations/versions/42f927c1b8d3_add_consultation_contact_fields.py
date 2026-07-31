"""add consultation contact fields

Revision ID: 42f927c1b8d3
Revises: 9b08a6f4c2d1
Create Date: 2026-08-01
"""

from alembic import op
import sqlalchemy as sa

revision = "42f927c1b8d3"
down_revision = "9b08a6f4c2d1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("consultation_request", sa.Column("contact_name", sa.String(length=100), nullable=False))
    op.add_column("consultation_request", sa.Column("contact_phone", sa.String(length=20), nullable=False))
    op.add_column("consultation_request", sa.Column("contact_email", sa.String(length=100), nullable=False))
    op.add_column("consultation_request", sa.Column("consultation_method", sa.String(length=20), nullable=False))
    op.add_column("consultation_request", sa.Column("preferred_time", sa.String(length=100), nullable=True))
    op.add_column("consultation_request", sa.Column("preferred_branch", sa.String(length=100), nullable=True))
    op.add_column("consultation_request", sa.Column("memo", sa.String(length=1000), nullable=True))
    op.add_column("consultation_request", sa.Column("consented_at", sa.DateTime(), nullable=False))
    op.add_column("consultation_request", sa.Column("policy_version", sa.String(length=30), nullable=False))


def downgrade() -> None:
    for column in ("policy_version", "consented_at", "memo", "preferred_branch", "preferred_time", "consultation_method", "contact_email", "contact_phone", "contact_name"):
        op.drop_column("consultation_request", column)
