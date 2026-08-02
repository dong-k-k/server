from alembic import op
import sqlalchemy as sa

revision = "a1c9f0e2b7d4"
down_revision = "42f927c1b8d3"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_names = inspector.get_table_names()

    # 1. product_master를 참조하는 모든 테이블의 FK 제거 (product_match_item, consultation_request_product 등)
    for table_name in table_names:
        for fk in inspector.get_foreign_keys(table_name):
            if fk.get("referred_table") == "product_master":
                op.drop_constraint(fk["name"], table_name, type_="foreignkey")

    # 2. product_match_item 컬럼 정리
    columns = {c["name"] for c in inspector.get_columns("product_match_item")}

    if "verdict" in columns and "eligibility_status" not in columns:
        op.alter_column("product_match_item", "verdict", new_column_name="eligibility_status", type_=sa.String(20))

    if "reason_text" in columns:
        op.alter_column("product_match_item", "reason_text", type_=sa.String(1000))

    if "product_name" not in columns:
        op.add_column("product_match_item", sa.Column("product_name", sa.String(100), nullable=False, server_default=""))
        op.alter_column("product_match_item", "product_name", server_default=None)
    if "provider" not in columns:
        op.add_column("product_match_item", sa.Column("provider", sa.String(50), nullable=False, server_default=""))
        op.alter_column("product_match_item", "provider", server_default=None)
    if "recommended_hedge_amount_krw" not in columns:
        op.add_column("product_match_item", sa.Column("recommended_hedge_amount_krw", sa.Numeric(18, 2), nullable=True))

    # 3. 로컬 상품 테이블 제거 (자식인 eligibility_rule 먼저)
    if "eligibility_rule" in table_names:
        op.drop_table("eligibility_rule")
    if "product_master" in table_names:
        op.drop_table("product_master")


def downgrade():
    pass