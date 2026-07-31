"""create application tables

Revision ID: 9b08a6f4c2d1
Revises: 55a93184ea6d
Create Date: 2026-08-01
"""

from alembic import op

revision = "9b08a6f4c2d1"
down_revision = "55a93184ea6d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    from app.profile import models as profile_models
    from app.contract import models as contract_models
    from app.risk import models as risk_models
    from app.risk_profile import models as risk_profile_models
    from app.product import models as product_models
    from app.strategy import models as strategy_models
    from app.consultation import models as consultation_models
    from app.country_risk import models as country_risk_models
    from app.core.db import Base

    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    from app.core.db import Base

    Base.metadata.drop_all(bind=op.get_bind())
