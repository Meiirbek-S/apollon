"""create static analysis results table"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "20260404_0003"
down_revision = "20260404_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE risklevel AS ENUM ('SAFE', 'SUSPICIOUS', 'MALWARE-LIKE');
        EXCEPTION
            WHEN duplicate_object THEN NULL;
        END $$;
        """
    )

    op.create_table(
        "static_analysis_results",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("submission_id", sa.Integer(), sa.ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("md5", sa.String(length=32), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("mime_type", sa.String(length=255), nullable=False),
        sa.Column(
            "risk_level",
            postgresql.ENUM("SAFE", "SUSPICIOUS", "MALWARE-LIKE", name="risklevel", create_type=False),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_static_analysis_results_submission_id", "static_analysis_results", ["submission_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_static_analysis_results_submission_id", table_name="static_analysis_results")
    op.drop_table("static_analysis_results")
    op.execute("DROP TYPE IF EXISTS risklevel")
