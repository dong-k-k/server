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
    # NOTE: 9b08a6f4c2d1이 Base.metadata.create_all()로 테이블을 생성하는데,
    # 그 시점 모델에 이미 이 필드들이 포함돼 있어서 새 DB에서는 이미 존재함.
    # 컬럼이 없는 환경(과거 로컬 DB 등)에서만 방어적으로 추가.
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_columns = {col["name"] for col in inspector.get_columns("consultation_request")}
    columns_to_add = [
        ("contact_name", sa.String(length=100), False),
        ("contact_phone", sa.String(length=20), False),
        ("contact_email", sa.String(length=100), False),
        ("consultation_method", sa.String(length=20), False),
        ("preferred_time", sa.String(length=100), True),
        ("preferred_branch", sa.String(length=100), True),
        ("memo", sa.String(length=1000), True),
        ("consented_at", sa.DateTime(), False),
        ("policy_version", sa.String(length=30), False),
    ]
    for name, col_type, nullable in columns_to_add:
        if name not in existing_columns:
            op.add_column("consultation_request", sa.Column(name, col_type, nullable=nullable))


def downgrade() -> None:
    pass