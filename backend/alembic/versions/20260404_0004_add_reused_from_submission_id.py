"""add reused_from_submission_id to submissions"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260404_0004"
down_revision = "20260404_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("submissions", sa.Column("reused_from_submission_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_submissions_reused_from_submission_id",
        "submissions",
        "submissions",
        ["reused_from_submission_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_submissions_reused_from_submission_id", "submissions", ["reused_from_submission_id"])


def downgrade() -> None:
    op.drop_index("ix_submissions_reused_from_submission_id", table_name="submissions")
    op.drop_constraint("fk_submissions_reused_from_submission_id", "submissions", type_="foreignkey")
    op.drop_column("submissions", "reused_from_submission_id")
