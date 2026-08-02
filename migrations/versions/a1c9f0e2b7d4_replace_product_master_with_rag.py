from alembic import op
import sqlalchemy as sa

revision = "a1c9f0e2b7d4"
down_revision = "42f927c1b8d3"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {c["name"] for c in inspector.get_columns("product_match_item")}
    fks = inspector.get_foreign_keys("product_match_item")

    # 1. product_id → product_master FK 제거 (RAG productId는 우리 DB에 없는 값이라 FK로 걸면 안 됨)
    for fk in fks:
        if fk.get("referred_table") == "product_master":
            op.drop_constraint(fk["name"], "product_match_item", type_="foreignkey")

    # 2. verdict → eligibility_status로 이름 변경
    if "verdict" in columns and "eligibility_status" not in columns:
        op.alter_column("product_match_item", "verdict", new_column_name="eligibility_status", type_=sa.String(20))

    # 3. reason_text 길이 확장 (RAG의 recommendationReasons는 여러 문장 합쳐서 길어질 수 있음)
    if "reason_text" in columns:
        op.alter_column("product_match_item", "reason_text", type_=sa.String(1000))

    # 4. 신규 컬럼 추가 (기존 행 채우기용 기본값 후 제거)
    if "product_name" not in columns:
        op.add_column("product_match_item", sa.Column("product_name", sa.String(100), nullable=False, server_default=""))
        op.alter_column("product_match_item", "product_name", server_default=None)
    if "provider" not in columns:
        op.add_column("product_match_item", sa.Column("provider", sa.String(50), nullable=False, server_default=""))
        op.alter_column("product_match_item", "provider", server_default=None)
    if "recommended_hedge_amount_krw" not in columns:
        op.add_column("product_match_item", sa.Column("recommended_hedge_amount_krw", sa.Numeric(18, 2), nullable=True))

    # 5. 로컬 상품 테이블 제거 (자식인 eligibility_rule 먼저)
    table_names = inspector.get_table_names()
    if "eligibility_rule" in table_names:
        op.drop_table("eligibility_rule")
    if "product_master" in table_names:
        op.drop_table("product_master")


def downgrade():
    pass