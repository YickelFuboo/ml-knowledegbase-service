BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> b14572ee46d9

CREATE TABLE knowledgebase (
    id VARCHAR(32) NOT NULL, 
    name VARCHAR(128) NOT NULL, 
    description TEXT, 
    language VARCHAR(32), 
    owner_id VARCHAR(32) NOT NULL, 
    tenant_id VARCHAR(32), 
    doc_num INTEGER DEFAULT '0', 
    embd_provider_name VARCHAR(32), 
    embd_model_name VARCHAR(32), 
    rerank_provider_name VARCHAR(32), 
    rerank_model_name VARCHAR(32), 
    parser_id VARCHAR(32) DEFAULT 'general' NOT NULL, 
    parser_config JSON NOT NULL, 
    page_rank INTEGER DEFAULT '0', 
    status VARCHAR(1) DEFAULT '1', 
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, 
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, 
    PRIMARY KEY (id)
);

COMMENT ON COLUMN knowledgebase.id IS '涓婚敭';

COMMENT ON COLUMN knowledgebase.name IS '鐭ヨ瘑搴撳悕绉?;

COMMENT ON COLUMN knowledgebase.description IS '鐭ヨ瘑搴撴弿杩?;

COMMENT ON COLUMN knowledgebase.language IS 'English|Chinese';

COMMENT ON COLUMN knowledgebase.owner_id IS '鎵€鏈夎€呯敤鎴稩D';

COMMENT ON COLUMN knowledgebase.tenant_id IS '鎵€灞炵鎴稩D';

COMMENT ON COLUMN knowledgebase.embd_provider_name IS '榛樿宓屽叆妯″瀷渚涘簲鍟嗗悕绉?;

COMMENT ON COLUMN knowledgebase.embd_model_name IS '榛樿宓屽叆妯″瀷鍚嶇О';

COMMENT ON COLUMN knowledgebase.rerank_provider_name IS '榛樿閲嶆帓搴忔ā鍨嬩緵搴斿晢鍚嶇О';

COMMENT ON COLUMN knowledgebase.rerank_model_name IS '榛樿閲嶆帓搴忔ā鍨嬪悕绉?;

COMMENT ON COLUMN knowledgebase.parser_id IS '瑙ｆ瀽鍣ㄧ被鍨?;

COMMENT ON COLUMN knowledgebase.parser_config IS '瑙ｆ瀽鍣ㄩ厤缃?JSON鏍煎紡)';

COMMENT ON COLUMN knowledgebase.page_rank IS '椤甸潰鎺掑悕绠楁硶寮哄害锛?琛ㄧず绂佺敤锛?-100琛ㄧず鍚敤涓斿己搴﹂€掑';

COMMENT ON COLUMN knowledgebase.status IS '鐘舵€?0:鏃犳晥, 1:鏈夋晥)';

CREATE INDEX ix_knowledgebase_name ON knowledgebase (name);

CREATE INDEX ix_knowledgebase_language ON knowledgebase (language);

CREATE INDEX ix_knowledgebase_owner_id ON knowledgebase (owner_id);

CREATE INDEX ix_knowledgebase_tenant_id ON knowledgebase (tenant_id);

CREATE INDEX ix_knowledgebase_doc_num ON knowledgebase (doc_num);

CREATE INDEX ix_knowledgebase_embd_provider_name ON knowledgebase (embd_provider_name);

CREATE INDEX ix_knowledgebase_embd_model_name ON knowledgebase (embd_model_name);

CREATE INDEX ix_knowledgebase_rerank_provider_name ON knowledgebase (rerank_provider_name);

CREATE INDEX ix_knowledgebase_rerank_model_name ON knowledgebase (rerank_model_name);

CREATE INDEX ix_knowledgebase_status ON knowledgebase (status);

CREATE TYPE processstatus AS ENUM ('init', 'chunking', 'raptoring', 'graphing', 'parsed', 'failed');

CREATE TABLE documents (
    id VARCHAR(36) NOT NULL, 
    kb_id VARCHAR(36) NOT NULL, 
    name VARCHAR(255) NOT NULL, 
    description TEXT, 
    type VARCHAR(20) DEFAULT 'pdf' NOT NULL, 
    suffix VARCHAR(10), 
    file_id VARCHAR(500), 
    size INTEGER DEFAULT '0', 
    parser_id VARCHAR(50) DEFAULT 'general' NOT NULL, 
    parser_config JSON, 
    meta_fields JSON, 
    thumbnail_id VARCHAR(500), 
    source_type VARCHAR(20) DEFAULT 'upload', 
    process_status processstatus DEFAULT 'init', 
    created_by VARCHAR(36) NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, 
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(kb_id) REFERENCES knowledgebase (id)
);

COMMENT ON COLUMN documents.id IS '鏂囨。ID';

COMMENT ON COLUMN documents.kb_id IS '鐭ヨ瘑搴揑D';

COMMENT ON COLUMN documents.name IS '鏂囨。鍚嶇О';

COMMENT ON COLUMN documents.description IS '鏂囨。鎻忚堪';

COMMENT ON COLUMN documents.type IS '鏂囨。绫诲瀷';

COMMENT ON COLUMN documents.suffix IS '鏂囦欢鎵╁睍鍚?;

COMMENT ON COLUMN documents.file_id IS '鏂囦欢鍞竴鏍囪瘑绗?;

COMMENT ON COLUMN documents.size IS '鏂囦欢澶у皬(瀛楄妭)';

COMMENT ON COLUMN documents.parser_id IS '瑙ｆ瀽鍣ㄧ被鍨?;

COMMENT ON COLUMN documents.parser_config IS '瑙ｆ瀽鍣ㄩ厤缃?JSON)';

COMMENT ON COLUMN documents.meta_fields IS '鏂囨。鍏冩暟鎹瓧娈?JSON)';

COMMENT ON COLUMN documents.thumbnail_id IS '缂╃暐鍥綢D';

COMMENT ON COLUMN documents.source_type IS '鏂囦欢鏉ユ簮';

COMMENT ON COLUMN documents.process_status IS '鏂囨。澶勭悊鐘舵€?;

COMMENT ON COLUMN documents.created_by IS '鍒涘缓鑰匢D';

COMMENT ON COLUMN documents.created_at IS '鍒涘缓鏃堕棿';

COMMENT ON COLUMN documents.updated_at IS '鏇存柊鏃堕棿';

INSERT INTO alembic_version (version_num) VALUES ('b14572ee46d9') RETURNING alembic_version.version_num;

COMMIT;

