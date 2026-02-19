"""agent_sessions: messages 改为 JSON 列，其余为独立字段

Revision ID: 002
Revises: 001
Create Date: 2025-02-01 00:00:00.000000

"""
from typing import Sequence, Union
import json
from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, Sequence[str], None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    # 1. 添加新列（先 nullable 便于从 payload 回填）
    op.add_column("agent_sessions", sa.Column("description", sa.Text(), nullable=True, comment="会话描述"))
    op.add_column("agent_sessions", sa.Column("session_type", sa.String(64), nullable=True, comment="会话类型"))
    op.add_column("agent_sessions", sa.Column("user_id", sa.String(128), nullable=True, comment="用户ID"))
    op.add_column("agent_sessions", sa.Column("llm_name", sa.String(128), nullable=True, comment="模型名称"))
    op.add_column("agent_sessions", sa.Column("messages", sa.JSON(), nullable=True, comment="消息列表 JSON"))
    op.add_column("agent_sessions", sa.Column("metadata", sa.JSON(), nullable=True, comment="元数据 JSON"))
    op.add_column("agent_sessions", sa.Column("last_updated", sa.DateTime(), nullable=True, comment="最后更新时间"))

    # 2. 从 payload 回填
    rows = conn.execute(sa.text("SELECT session_id, payload, created_at, updated_at FROM agent_sessions")).fetchall()
    for row in rows:
        sid, payload_str, created_at, updated_at = row
        try:
            data = json.loads(payload_str)
            desc = data.get("description")
            stype = data.get("session_type") or "chat"
            uid = data.get("user_id") or ""
            llm = data.get("llm_name") or "default"
            msgs = data.get("messages") or []
            meta = data.get("metadata")
            last_up = data.get("last_updated") or updated_at
            if isinstance(last_up, str):
                last_up = updated_at
            conn.execute(
                sa.text("""
                    UPDATE agent_sessions SET
                    description = :desc, session_type = :stype, user_id = :uid,
                    llm_name = :llm, messages = :msgs, metadata = :meta, last_updated = :last_up
                    WHERE session_id = :sid
                """),
                {"desc": desc, "stype": stype, "uid": uid, "llm": llm, "msgs": msgs, "meta": meta, "last_up": last_up, "sid": sid}
            )
        except Exception:
            conn.execute(
                sa.text("""
                    UPDATE agent_sessions SET
                    session_type = 'chat', user_id = '', llm_name = 'default',
                    messages = '[]', last_updated = updated_at
                    WHERE session_id = :sid
                """),
                {"sid": sid}
            )

    # 3. 删除 payload、updated_at
    op.drop_column("agent_sessions", "payload")
    op.drop_column("agent_sessions", "updated_at")

    # 4. 非空约束
    op.alter_column("agent_sessions", "session_type", nullable=False)
    op.alter_column("agent_sessions", "user_id", nullable=False)
    op.alter_column("agent_sessions", "llm_name", nullable=False)
    op.alter_column("agent_sessions", "messages", nullable=False)
    op.alter_column("agent_sessions", "last_updated", nullable=False)


def downgrade() -> None:
    op.add_column("agent_sessions", sa.Column("payload", sa.Text(), nullable=True))
    op.add_column("agent_sessions", sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False))

    conn = op.get_bind()
    rows = conn.execute(sa.text(
        "SELECT session_id, description, session_type, user_id, llm_name, messages, metadata, created_at, last_updated FROM agent_sessions"
    )).fetchall()
    for row in rows:
        sid, desc, stype, uid, llm, msgs, meta, created_at, last_up = row
        payload = json.dumps({
            "session_id": sid,
            "description": desc,
            "session_type": stype,
            "user_id": uid,
            "llm_name": llm,
            "messages": msgs if isinstance(msgs, list) else (json.loads(msgs) if msgs else []),
            "metadata": meta if isinstance(meta, dict) else (json.loads(meta) if meta else {}),
            "created_at": created_at.isoformat() if hasattr(created_at, "isoformat") else str(created_at),
            "last_updated": last_up.isoformat() if hasattr(last_up, "isoformat") else str(last_up),
        }, ensure_ascii=False)
        conn.execute(sa.text("UPDATE agent_sessions SET payload = :p WHERE session_id = :sid"), {"p": payload, "sid": sid})

    op.alter_column("agent_sessions", "payload", nullable=False)
    op.drop_column("agent_sessions", "description")
    op.drop_column("agent_sessions", "session_type")
    op.drop_column("agent_sessions", "user_id")
    op.drop_column("agent_sessions", "llm_name")
    op.drop_column("agent_sessions", "messages")
    op.drop_column("agent_sessions", "metadata")
    op.drop_column("agent_sessions", "last_updated")
