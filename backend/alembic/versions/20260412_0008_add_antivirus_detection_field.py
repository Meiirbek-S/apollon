"""add antivirus_detection field to static analysis results"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260412_0008"
down_revision = "20260405_0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "static_analysis_results",
        sa.Column("antivirus_detection", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
    )
    op.alter_column("static_analysis_results", "antivirus_detection", server_default=None)


def downgrade() -> None:
    op.drop_column("static_analysis_results", "antivirus_detection")
