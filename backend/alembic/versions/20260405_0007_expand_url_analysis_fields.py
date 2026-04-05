"""expand URL analysis fields for richer MVP report"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260405_0007"
down_revision = "20260404_0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("url_analysis_results", sa.Column("scheme", sa.String(length=16), nullable=False, server_default="http"))
    op.add_column("url_analysis_results", sa.Column("hostname", sa.String(length=255), nullable=False, server_default=""))
    op.add_column("url_analysis_results", sa.Column("path", sa.String(length=2048), nullable=False, server_default="/"))
    op.add_column("url_analysis_results", sa.Column("query_present", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("url_analysis_results", sa.Column("port", sa.Integer(), nullable=True))
    op.add_column("url_analysis_results", sa.Column("dns_resolved", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("url_analysis_results", sa.Column("final_url", sa.String(length=2048), nullable=True))
    op.add_column("url_analysis_results", sa.Column("redirect_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("url_analysis_results", sa.Column("risk_score", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("url_analysis_results", sa.Column("risk_indicators", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")))
    op.add_column("url_analysis_results", sa.Column("verdict_reason", sa.Text(), nullable=False, server_default=""))
    op.add_column(
        "url_analysis_results",
        sa.Column("analyzed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.execute(
        """
        UPDATE url_analysis_results
        SET
          scheme = CASE WHEN uses_https THEN 'https' ELSE 'http' END,
          hostname = domain,
          path = '/',
          query_present = false,
          dns_resolved = CASE WHEN resolved_ip IS NULL THEN false ELSE true END,
          final_url = normalized_url,
          redirect_count = 0,
          risk_score = CASE risk_level
                        WHEN 'SAFE' THEN 10
                        WHEN 'SUSPICIOUS' THEN 35
                        ELSE 70
                       END,
          risk_indicators = CASE
                              WHEN uses_https THEN '["Сайт использует HTTPS"]'::json
                              ELSE '["URL не использует HTTPS"]'::json
                            END,
          verdict_reason = CASE risk_level
                            WHEN 'SAFE' THEN 'SAFE: baseline URL analysis completed'
                            WHEN 'SUSPICIOUS' THEN 'SUSPICIOUS: baseline URL analysis detected risk signals'
                            ELSE 'MALWARE-LIKE: baseline URL analysis detected high-risk signals'
                           END,
          analyzed_at = created_at
        """
    )

    op.alter_column("url_analysis_results", "scheme", server_default=None)
    op.alter_column("url_analysis_results", "hostname", server_default=None)
    op.alter_column("url_analysis_results", "path", server_default=None)
    op.alter_column("url_analysis_results", "query_present", server_default=None)
    op.alter_column("url_analysis_results", "dns_resolved", server_default=None)
    op.alter_column("url_analysis_results", "redirect_count", server_default=None)
    op.alter_column("url_analysis_results", "risk_score", server_default=None)
    op.alter_column("url_analysis_results", "risk_indicators", server_default=None)
    op.alter_column("url_analysis_results", "verdict_reason", server_default=None)
    op.alter_column("url_analysis_results", "analyzed_at", server_default=None)


def downgrade() -> None:
    op.drop_column("url_analysis_results", "analyzed_at")
    op.drop_column("url_analysis_results", "verdict_reason")
    op.drop_column("url_analysis_results", "risk_indicators")
    op.drop_column("url_analysis_results", "risk_score")
    op.drop_column("url_analysis_results", "redirect_count")
    op.drop_column("url_analysis_results", "final_url")
    op.drop_column("url_analysis_results", "dns_resolved")
    op.drop_column("url_analysis_results", "port")
    op.drop_column("url_analysis_results", "query_present")
    op.drop_column("url_analysis_results", "path")
    op.drop_column("url_analysis_results", "hostname")
    op.drop_column("url_analysis_results", "scheme")
