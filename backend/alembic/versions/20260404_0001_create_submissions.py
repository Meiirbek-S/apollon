"""create submissions table"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "20260404_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Idempotent for partially failed runs:
    # if enum type was created in a previous failed attempt, this won't fail.
    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE submissiontype AS ENUM ('FILE', 'URL');
        EXCEPTION
            WHEN duplicate_object THEN NULL;
        END $$;
        """
    )

    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE submissionstatus AS ENUM ('QUEUED', 'PROCESSING', 'DONE', 'FAILED');
        EXCEPTION
            WHEN duplicate_object THEN NULL;
        END $$;
        """
    )

    op.create_table(
        "submissions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "source_type",
            postgresql.ENUM("FILE", "URL", name="submissiontype", create_type=False),
            nullable=False,
        ),
        sa.Column("filename", sa.String(length=512), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(
                "QUEUED",
                "PROCESSING",
                "DONE",
                "FAILED",
                name="submissionstatus",
                create_type=False,
            ),
            nullable=False,
            server_default="QUEUED",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_submissions_sha256", "submissions", ["sha256"])


def downgrade() -> None:
    op.drop_index("ix_submissions_sha256", table_name="submissions")
    op.drop_table("submissions")

    op.execute("DROP TYPE IF EXISTS submissionstatus")
    op.execute("DROP TYPE IF EXISTS submissiontype")
