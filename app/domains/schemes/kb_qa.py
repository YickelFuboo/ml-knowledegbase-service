from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ChatMessage(BaseModel):
    """聊天消息模型"""
    role: str = Field(..., description="消息角色: user, assistant, system")
    content: str = Field(..., description="消息内容")

    def to_dict(self) -> Dict[str, str]:
        """转换为字典格式"""
        return {"role": self.role, "content": self.content}

class KbQueryRequest(BaseModel):
    """知识库查询请求模型"""
    model_config = ConfigDict(protected_namespaces=())
    question: str = Field(..., description="用户问题")
    session_id: Optional[str] = Field(None, description="会话ID，传入则从会话获取历史记录")
    kb_ids: List[str] = Field(..., description="知识库ID列表", min_items=1)
    doc_ids: Optional[List[str]] = Field(None, description="指定检索的文档ID列表")
    # 功能开关
    enable_quote: bool = Field(True, description="是否启用引用")
    enable_multi_questions: bool = Field(False, description="是否启用多问题生成")
    enable_keyword_extraction: bool = Field(False, description="是否启用关键词提取")
    enable_deep_research: bool = Field(False, description="是否启用深度研究")
    enable_web_search: bool = Field(False, description="是否启用网络搜索")
    enable_knowledge_graph: bool = Field(False, description="是否启用知识图谱检索")
    target_language: Optional[str] = Field(None, description="目标语言代码，如：zh、en、ja等")
    model_provider: Optional[str] = Field(None, description="指定Chat模型提供商，不传则使用默认")
    model_name: Optional[str] = Field(None, description="指定Chat模型名称，不传则使用默认")

class DocumentReference(BaseModel):
    """文档引用模型"""
    doc_id: str = Field(..., description="文档ID")
    doc_name: str = Field(..., description="文档名称")
    count: int = Field(..., description="引用次数")


class ChunkInfo(BaseModel):
    """文档片段信息模型 - 与chunks_format函数输出格式一致"""
    id: Optional[str] = Field(None, description="片段ID")
    content: Optional[str] = Field(None, description="片段内容")
    document_id: Optional[str] = Field(None, description="文档ID")
    document_name: Optional[str] = Field(None, description="文档名称")
    dataset_id: Optional[Any] = Field(None, description="数据集ID")
    image_id: Optional[Any] = Field(None, description="图像ID")
    positions: Optional[Any] = Field(None, description="位置信息")
    url: Optional[str] = Field(None, description="URL")
    similarity: Optional[float] = Field(None, description="相似度分数")
    vector_similarity: Optional[float] = Field(None, description="向量相似度")
    term_similarity: Optional[float] = Field(None, description="词汇相似度")
    doc_type: Optional[str] = Field(None, description="文档类型")


class QaReference(BaseModel):
    """问答引用信息模型"""
    total: Optional[int] = Field(0, description="总检索数量")
    chunks: Optional[List[ChunkInfo]] = Field(default_factory=list, description="检索到的文档片段")
    doc_aggs: Optional[List[DocumentReference]] = Field(default_factory=list, description="文档聚合信息")


class QaResponse(BaseModel):
    """问答响应模型"""
    answer: str = Field(..., description="回答内容")
    reference: Optional[QaReference] = Field(None, description="引用信息")
    prompt: Optional[str] = Field(None, description="使用的提示词")
    created_at: Optional[float] = Field(None, description="创建时间戳")
    session_id: Optional[str] = Field(None, description="会话ID，与请求中的 session_id 一致")
