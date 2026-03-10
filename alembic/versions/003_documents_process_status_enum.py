"""documents: process_status 从 VARCHAR 改为 processstatus 枚举类型

Revision ID: 003
Revises: 002
Create Date: 2026-03-10 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

revision: str = "003"
down_revision: Union[str, Sequence[str], None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    op.execute("CREATE TYPE processstatus AS ENUM ('init', 'chunking', 'raptoring', 'graphing', 'parsed', 'failed')")
    op.execute(
        "ALTER TABLE documents ALTER COLUMN process_status TYPE processstatus "
        "USING CASE WHEN process_status IS NULL THEN NULL::processstatus ELSE process_status::text::processstatus END"
    )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    op.execute(
        "ALTER TABLE documents ALTER COLUMN process_status TYPE VARCHAR(20) "
        "USING process_status::text"
    )
    op.execute("DROP TYPE processstatus")
