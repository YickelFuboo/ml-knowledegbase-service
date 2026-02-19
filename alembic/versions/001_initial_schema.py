"""initial schema: knowledgebase, documents, agent_sessions

Revision ID: 001
Revises:
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "knowledgebase",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False, comment="知识库名称"),
        sa.Column("description", sa.Text(), nullable=True, comment="知识库描述"),
        sa.Column("language", sa.String(32), nullable=True, comment="English|Chinese"),
        sa.Column("owner_id", sa.String(36), nullable=False, comment="所有者用户ID"),
        sa.Column("tenant_id", sa.String(36), nullable=True, comment="所属租户ID"),
        sa.Column("doc_num", sa.Integer(), default=0),
        sa.Column("embd_provider_name", sa.String(32), nullable=True),
        sa.Column("embd_model_name", sa.String(32), nullable=True),
        sa.Column("rerank_provider_name", sa.String(32), nullable=True),
        sa.Column("rerank_model_name", sa.String(32), nullable=True),
        sa.Column("parser_id", sa.String(32), nullable=False),
        sa.Column("parser_config", sa.JSON(), nullable=False),
        sa.Column("page_rank", sa.Integer(), default=0),
        sa.Column("status", sa.String(1), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_knowledgebase_name", "knowledgebase", ["name"])
    op.create_index("ix_knowledgebase_language", "knowledgebase", ["language"])
    op.create_index("ix_knowledgebase_owner_id", "knowledgebase", ["owner_id"])
    op.create_index("ix_knowledgebase_tenant_id", "knowledgebase", ["tenant_id"])
    op.create_index("ix_knowledgebase_doc_num", "knowledgebase", ["doc_num"])
    op.create_index("ix_knowledgebase_embd_provider_name", "knowledgebase", ["embd_provider_name"])
    op.create_index("ix_knowledgebase_embd_model_name", "knowledgebase", ["embd_model_name"])
    op.create_index("ix_knowledgebase_rerank_provider_name", "knowledgebase", ["rerank_provider_name"])
    op.create_index("ix_knowledgebase_rerank_model_name", "knowledgebase", ["rerank_model_name"])
    op.create_index("ix_knowledgebase_status", "knowledgebase", ["status"])

    op.create_table(
        "documents",
        sa.Column("id", sa.String(36), primary_key=True, comment="文档ID"),
        sa.Column("kb_id", sa.String(36), sa.ForeignKey("knowledgebase.id"), nullable=False, comment="知识库ID"),
        sa.Column("name", sa.String(255), nullable=False, comment="文档名称"),
        sa.Column("description", sa.Text(), nullable=True, comment="文档描述"),
        sa.Column("type", sa.String(20), nullable=False, comment="文档类型"),
        sa.Column("suffix", sa.String(10), nullable=True, comment="文件扩展名"),
        sa.Column("file_id", sa.String(500), nullable=True, comment="文件唯一标识符"),
        sa.Column("size", sa.Integer(), default=0, comment="文件大小(字节)"),
        sa.Column("parser_id", sa.String(50), nullable=False, comment="解析器类型"),
        sa.Column("parser_config", sa.JSON(), nullable=True, comment="解析器配置(JSON)"),
        sa.Column("meta_fields", sa.JSON(), nullable=True, comment="文档元数据字段(JSON)"),
        sa.Column("thumbnail_id", sa.String(500), nullable=True, comment="缩略图ID"),
        sa.Column("source_type", sa.String(20), nullable=True, comment="文件来源"),
        sa.Column("process_status", sa.String(20), nullable=True, comment="文档处理状态"),
        sa.Column("created_by", sa.String(36), nullable=False, comment="创建者ID"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False, comment="创建时间"),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False, comment="更新时间"),
    )

    op.create_table(
        "agent_sessions",
        sa.Column("session_id", sa.String(128), primary_key=True, comment="会话ID"),
        sa.Column("payload", sa.Text(), nullable=False, comment="Session JSON"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("agent_sessions")
    op.drop_table("documents")
    op.drop_table("knowledgebase")
