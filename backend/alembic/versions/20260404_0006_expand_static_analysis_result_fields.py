"""expand static analysis result fields"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260404_0006"
down_revision = "20260404_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("static_analysis_results", sa.Column("original_filename", sa.String(length=512), nullable=True))
    op.add_column("static_analysis_results", sa.Column("extension", sa.String(length=32), nullable=True))
    op.add_column("static_analysis_results", sa.Column("extension_mismatch", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("static_analysis_results", sa.Column("risk_score", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("static_analysis_results", sa.Column("risk_indicators", sa.JSON(), nullable=False, server_default="[]"))
    op.add_column("static_analysis_results", sa.Column("verdict_reason", sa.Text(), nullable=False, server_default=""))

    op.add_column("static_analysis_results", sa.Column("is_pe", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("static_analysis_results", sa.Column("machine_type", sa.String(length=64), nullable=True))
    op.add_column("static_analysis_results", sa.Column("compile_timestamp", sa.String(length=64), nullable=True))
    op.add_column("static_analysis_results", sa.Column("entry_point", sa.String(length=32), nullable=True))
    op.add_column("static_analysis_results", sa.Column("image_base", sa.String(length=32), nullable=True))
    op.add_column("static_analysis_results", sa.Column("pe_sections", sa.JSON(), nullable=False, server_default="[]"))
    op.add_column("static_analysis_results", sa.Column("imported_functions", sa.JSON(), nullable=False, server_default="[]"))
    op.add_column("static_analysis_results", sa.Column("suspicious_imports", sa.JSON(), nullable=False, server_default="[]"))

    op.execute("UPDATE static_analysis_results SET original_filename = '' WHERE original_filename IS NULL")
    op.execute("UPDATE static_analysis_results SET extension = '' WHERE extension IS NULL")

    op.alter_column("static_analysis_results", "original_filename", nullable=False)
    op.alter_column("static_analysis_results", "extension", nullable=False)


def downgrade() -> None:
    op.drop_column("static_analysis_results", "suspicious_imports")
    op.drop_column("static_analysis_results", "imported_functions")
    op.drop_column("static_analysis_results", "pe_sections")
    op.drop_column("static_analysis_results", "image_base")
    op.drop_column("static_analysis_results", "entry_point")
    op.drop_column("static_analysis_results", "compile_timestamp")
    op.drop_column("static_analysis_results", "machine_type")
    op.drop_column("static_analysis_results", "is_pe")
    op.drop_column("static_analysis_results", "verdict_reason")
    op.drop_column("static_analysis_results", "risk_indicators")
    op.drop_column("static_analysis_results", "risk_score")
    op.drop_column("static_analysis_results", "extension_mismatch")
    op.drop_column("static_analysis_results", "extension")
    op.drop_column("static_analysis_results", "original_filename")
