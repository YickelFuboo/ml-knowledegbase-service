"""kb owner_id tenant_id varchar36

Revision ID: c25683ab71f0
Revises: b14572ee46d9
Create Date: 2026-02-13

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "c25683ab71f0"
down_revision: Union[str, Sequence[str], None] = "b14572ee46d9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "knowledgebase",
        "owner_id",
        existing_type=sa.String(length=32),
        type_=sa.String(length=36),
        existing_nullable=False,
    )
    op.alter_column(
        "knowledgebase",
        "tenant_id",
        existing_type=sa.String(length=32),
        type_=sa.String(length=36),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "knowledgebase",
        "owner_id",
        existing_type=sa.String(length=36),
        type_=sa.String(length=32),
        existing_nullable=False,
    )
    op.alter_column(
        "knowledgebase",
        "tenant_id",
        existing_type=sa.String(length=36),
        type_=sa.String(length=32),
        existing_nullable=True,
    )
