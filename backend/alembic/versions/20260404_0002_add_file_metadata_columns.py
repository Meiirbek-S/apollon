"""add file metadata columns to submissions"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260404_0002"
down_revision = "20260404_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("submissions", sa.Column("content_type", sa.String(length=255), nullable=True))
    op.add_column("submissions", sa.Column("size_bytes", sa.Integer(), nullable=True))
    op.add_column("submissions", sa.Column("storage_key", sa.String(length=512), nullable=True))


def downgrade() -> None:
    op.drop_column("submissions", "storage_key")
    op.drop_column("submissions", "size_bytes")
    op.drop_column("submissions", "content_type")
