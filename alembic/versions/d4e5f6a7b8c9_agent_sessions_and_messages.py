"""agent_sessions_and_messages

Revision ID: d4e5f6a7b8c9
Revises: c25683ab71f0
Create Date: 2026-02-14

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, Sequence[str], None] = "c25683ab71f0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "agent_sessions",
        sa.Column("id", sa.String(length=36), nullable=False, comment="会话ID"),
        sa.Column("user_id", sa.String(length=36), nullable=False, comment="用户ID"),
        sa.Column("tenant_id", sa.String(length=36), nullable=True, comment="租户ID"),
        sa.Column("title", sa.String(length=256), nullable=True, comment="会话标题"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_agent_sessions_user_id"), "agent_sessions", ["user_id"], unique=False)
    op.create_index(op.f("ix_agent_sessions_tenant_id"), "agent_sessions", ["tenant_id"], unique=False)

    op.create_table(
        "agent_messages",
        sa.Column("id", sa.String(length=36), nullable=False, comment="消息ID"),
        sa.Column("session_id", sa.String(length=36), nullable=False, comment="所属会话ID"),
        sa.Column("role", sa.String(length=20), nullable=False, comment="角色: user / assistant / system"),
        sa.Column("content", sa.Text(), nullable=False, comment="消息内容"),
        sa.Column("seq", sa.Integer(), nullable=False, server_default="0", comment="会话内顺序"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["session_id"], ["agent_sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_agent_messages_session_id"), "agent_messages", ["session_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_agent_messages_session_id"), table_name="agent_messages")
    op.drop_table("agent_messages")
    op.drop_index(op.f("ix_agent_sessions_tenant_id"), table_name="agent_sessions")
    op.drop_index(op.f("ix_agent_sessions_user_id"), table_name="agent_sessions")
    op.drop_table("agent_sessions")
