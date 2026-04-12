"""add dynamic analysis workflow using docker/external providers"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260412_0008"
down_revision = "20260405_0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    dynamic_status_enum = sa.Enum(
        "NOT_REQUESTED",
        "QUEUED",
        "RUNNING",
        "DONE",
        "FAILED",
        name="dynamicanalysisstatus",
    )
    dynamic_status_enum.create(op.get_bind(), checkfirst=True)

    op.add_column("submissions", sa.Column("dynamic_requested", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column(
        "submissions",
        sa.Column("dynamic_status", dynamic_status_enum, nullable=False, server_default="NOT_REQUESTED"),
    )

    op.create_table(
        "dynamic_analysis_results",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("submission_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("sandbox_id", sa.String(length=128), nullable=True),
        sa.Column("risk_score", sa.Integer(), nullable=False),
        sa.Column("risk_level", sa.Enum("SAFE", "SUSPICIOUS", "MALWARE-LIKE", name="risklevel"), nullable=False),
        sa.Column("suspicious_actions", sa.JSON(), nullable=False),
        sa.Column("network_connections", sa.JSON(), nullable=False),
        sa.Column("file_changes", sa.JSON(), nullable=False),
        sa.Column("registry_changes", sa.JSON(), nullable=False),
        sa.Column("verdict_reason", sa.Text(), nullable=False),
        sa.Column("raw_report", sa.JSON(), nullable=False),
        sa.Column("analyzed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["submission_id"], ["submissions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_dynamic_analysis_results_submission_id"), "dynamic_analysis_results", ["submission_id"], unique=True)

    op.alter_column("submissions", "dynamic_requested", server_default=None)
    op.alter_column("submissions", "dynamic_status", server_default=None)


def downgrade() -> None:
    op.drop_index(op.f("ix_dynamic_analysis_results_submission_id"), table_name="dynamic_analysis_results")
    op.drop_table("dynamic_analysis_results")
    op.drop_column("submissions", "dynamic_status")
    op.drop_column("submissions", "dynamic_requested")

    dynamic_status_enum = sa.Enum(
        "NOT_REQUESTED",
        "QUEUED",
        "RUNNING",
        "DONE",
        "FAILED",
        name="dynamicanalysisstatus",
    )
    dynamic_status_enum.drop(op.get_bind(), checkfirst=True)
