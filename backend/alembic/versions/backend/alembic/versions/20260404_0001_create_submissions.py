"""create submissions table"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260404_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    submission_type = sa.Enum("FILE", "URL", name="submissiontype")
    submission_status = sa.Enum("QUEUED", "PROCESSING", "DONE", "FAILED", name="submissionstatus")

    submission_type.create(op.get_bind(), checkfirst=True)
    submission_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "submissions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_type", submission_type, nullable=False),
        sa.Column("filename", sa.String(length=512), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=True),
        sa.Column("status", submission_status, nullable=False, server_default="QUEUED"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_submissions_sha256", "submissions", ["sha256"])


def downgrade() -> None:
    op.drop_index("ix_submissions_sha256", table_name="submissions")
    op.drop_table("submissions")

    submission_status = sa.Enum("QUEUED", "PROCESSING", "DONE", "FAILED", name="submissionstatus")
    submission_type = sa.Enum("FILE", "URL", name="submissiontype")
    submission_status.drop(op.get_bind(), checkfirst=True)
    submission_type.drop(op.get_bind(), checkfirst=True)
