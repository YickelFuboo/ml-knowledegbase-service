"""initial_migration

Revision ID: b14572ee46d9
Revises: 
Create Date: 2026-02-12 15:41:01.608581

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql, mysql


# revision identifiers, used by Alembic.
revision: str = 'b14572ee46d9'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """创建初始表结构"""
    op.create_table(
        'knowledgebase',
        sa.Column('id', sa.String(length=32), nullable=False, comment='主键'),
        sa.Column('name', sa.String(length=128), nullable=False, comment='知识库名称'),
        sa.Column('description', sa.Text(), nullable=True, comment='知识库描述'),
        sa.Column('language', sa.String(length=32), nullable=True, comment='English|Chinese'),
        sa.Column('owner_id', sa.String(length=32), nullable=False, comment='所有者用户ID'),
        sa.Column('tenant_id', sa.String(length=32), nullable=True, comment='所属租户ID'),
        sa.Column('doc_num', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('embd_provider_name', sa.String(length=32), nullable=True, comment='默认嵌入模型供应商名称'),
        sa.Column('embd_model_name', sa.String(length=32), nullable=True, comment='默认嵌入模型名称'),
        sa.Column('rerank_provider_name', sa.String(length=32), nullable=True, comment='默认重排序模型供应商名称'),
        sa.Column('rerank_model_name', sa.String(length=32), nullable=True, comment='默认重排序模型名称'),
        sa.Column('parser_id', sa.String(length=32), nullable=False, server_default='general', comment='解析器类型'),
        sa.Column('parser_config', sa.JSON(), nullable=False, comment='解析器配置(JSON格式)'),
        sa.Column('page_rank', sa.Integer(), nullable=True, server_default='0', comment='页面排名算法强度，0表示禁用，1-100表示启用且强度递增'),
        sa.Column('status', sa.String(length=1), nullable=True, server_default='1', comment='状态(0:无效, 1:有效)'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_knowledgebase_name'), 'knowledgebase', ['name'], unique=False)
    op.create_index(op.f('ix_knowledgebase_language'), 'knowledgebase', ['language'], unique=False)
    op.create_index(op.f('ix_knowledgebase_owner_id'), 'knowledgebase', ['owner_id'], unique=False)
    op.create_index(op.f('ix_knowledgebase_tenant_id'), 'knowledgebase', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_knowledgebase_doc_num'), 'knowledgebase', ['doc_num'], unique=False)
    op.create_index(op.f('ix_knowledgebase_embd_provider_name'), 'knowledgebase', ['embd_provider_name'], unique=False)
    op.create_index(op.f('ix_knowledgebase_embd_model_name'), 'knowledgebase', ['embd_model_name'], unique=False)
    op.create_index(op.f('ix_knowledgebase_rerank_provider_name'), 'knowledgebase', ['rerank_provider_name'], unique=False)
    op.create_index(op.f('ix_knowledgebase_rerank_model_name'), 'knowledgebase', ['rerank_model_name'], unique=False)
    op.create_index(op.f('ix_knowledgebase_status'), 'knowledgebase', ['status'], unique=False)

    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        process_status_enum = postgresql.ENUM('init', 'chunking', 'raptoring', 'graphing', 'parsed', 'failed', name='processstatus', create_type=False)
        process_status_enum.create(bind, checkfirst=True)
        process_status_type = process_status_enum
    else:
        process_status_type = sa.String(length=20)

    op.create_table(
        'documents',
        sa.Column('id', sa.String(length=36), nullable=False, comment='文档ID'),
        sa.Column('kb_id', sa.String(length=36), nullable=False, comment='知识库ID'),
        sa.Column('name', sa.String(length=255), nullable=False, comment='文档名称'),
        sa.Column('description', sa.Text(), nullable=True, comment='文档描述'),
        sa.Column('type', sa.String(length=20), nullable=False, server_default='pdf', comment='文档类型'),
        sa.Column('suffix', sa.String(length=10), nullable=True, comment='文件扩展名'),
        sa.Column('file_id', sa.String(length=500), nullable=True, comment='文件唯一标识符'),
        sa.Column('size', sa.Integer(), nullable=True, server_default='0', comment='文件大小(字节)'),
        sa.Column('parser_id', sa.String(length=50), nullable=False, server_default='general', comment='解析器类型'),
        sa.Column('parser_config', sa.JSON(), nullable=True, comment='解析器配置(JSON)'),
        sa.Column('meta_fields', sa.JSON(), nullable=True, comment='文档元数据字段(JSON)'),
        sa.Column('thumbnail_id', sa.String(length=500), nullable=True, comment='缩略图ID'),
        sa.Column('source_type', sa.String(length=20), nullable=True, server_default='upload', comment='文件来源'),
        sa.Column('process_status', process_status_type, nullable=True, server_default='init', comment='文档处理状态'),
        sa.Column('created_by', sa.String(length=36), nullable=False, comment='创建者ID'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='更新时间'),
        sa.ForeignKeyConstraint(['kb_id'], ['knowledgebase.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """删除表结构"""
    op.drop_table('documents')
    op.drop_index(op.f('ix_knowledgebase_status'), table_name='knowledgebase')
    op.drop_index(op.f('ix_knowledgebase_rerank_model_name'), table_name='knowledgebase')
    op.drop_index(op.f('ix_knowledgebase_rerank_provider_name'), table_name='knowledgebase')
    op.drop_index(op.f('ix_knowledgebase_embd_model_name'), table_name='knowledgebase')
    op.drop_index(op.f('ix_knowledgebase_embd_provider_name'), table_name='knowledgebase')
    op.drop_index(op.f('ix_knowledgebase_doc_num'), table_name='knowledgebase')
    op.drop_index(op.f('ix_knowledgebase_tenant_id'), table_name='knowledgebase')
    op.drop_index(op.f('ix_knowledgebase_owner_id'), table_name='knowledgebase')
    op.drop_index(op.f('ix_knowledgebase_language'), table_name='knowledgebase')
    op.drop_index(op.f('ix_knowledgebase_name'), table_name='knowledgebase')
    op.drop_table('knowledgebase')
    
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        process_status_enum = postgresql.ENUM(name='processstatus', create_type=False)
        process_status_enum.drop(bind, checkfirst=True)
