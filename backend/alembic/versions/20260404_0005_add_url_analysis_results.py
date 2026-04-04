"""add URL analysis support"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "20260404_0005"
down_revision = "20260404_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("submissions", sa.Column("target_url", sa.String(length=2048), nullable=True))

    op.create_table(
        "url_analysis_results",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("submission_id", sa.Integer(), sa.ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("normalized_url", sa.String(length=2048), nullable=False),
        sa.Column("domain", sa.String(length=255), nullable=False),
        sa.Column("resolved_ip", sa.String(length=64), nullable=True),
        sa.Column("uses_https", sa.Boolean(), nullable=False),
        sa.Column(
            "risk_level",
            postgresql.ENUM("SAFE", "SUSPICIOUS", "MALWARE-LIKE", name="risklevel", create_type=False),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_url_analysis_results_submission_id", "url_analysis_results", ["submission_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_url_analysis_results_submission_id", table_name="url_analysis_results")
    op.drop_table("url_analysis_results")
    op.drop_column("submissions", "target_url")
