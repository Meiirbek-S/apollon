"""add yara result fields to static analysis report"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260412_0008"
down_revision = "20260405_0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("static_analysis_results", sa.Column("yara_matched", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("static_analysis_results", sa.Column("yara_match_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("static_analysis_results", sa.Column("yara_rule_names", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")))

    op.alter_column("static_analysis_results", "yara_matched", server_default=None)
    op.alter_column("static_analysis_results", "yara_match_count", server_default=None)
    op.alter_column("static_analysis_results", "yara_rule_names", server_default=None)


def downgrade() -> None:
    op.drop_column("static_analysis_results", "yara_rule_names")
    op.drop_column("static_analysis_results", "yara_match_count")
    op.drop_column("static_analysis_results", "yara_matched")
