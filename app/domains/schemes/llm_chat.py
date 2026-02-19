from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class ChatRequest(BaseModel):
    """LLM 聊天请求（可选会话，支持多轮）"""
    model_config = ConfigDict(protected_namespaces=())
    session_id: Optional[str] = Field(None, description="会话ID，不传则创建新会话")
    user_question: str = Field(..., description="用户问题")
    user_id: str = Field("anonymous", description="用户ID")
    model_provider: Optional[str] = Field(None, description="模型供应商，不传则用默认或 session 中模型")
    model_name: Optional[str] = Field(None, description="模型名称，不传则用默认或 session 中模型")
    enable_web_search: bool = Field(False, description="是否启用联网搜索")
    metadata: Optional[Dict[str, Any]] = Field(None, description="创建新会话时的元数据")


class ChatResponse(BaseModel):
    """LLM 聊天响应"""
    session_id: str = Field(..., description="会话ID")
    content: str = Field(..., description="助手回复内容")
    token_count: Optional[int] = Field(None, description="本次消耗 token 数")
