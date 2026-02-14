"""
知识库对话服务：统一问答入口，通过参数控制单轮/多轮、是否使用知识库及各类能力开关。
不修改 kb_qa_service 中的 single_ask / kb_query / chat，本模块为独立一套实现入口。
"""
import logging
from typing import AsyncGenerator, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemes.kb_qa import ChatMessage
from app.services.kb_qa_service import QAService


class KBChatService:
    """知识库对话服务：统一 ask 入口"""

    @staticmethod
    async def ask(
        session: AsyncSession,
        tenant_id: str,
        user_id: str,
        messages: List[ChatMessage],
        kb_ids: Optional[List[str]] = None,
        doc_ids: Optional[List[str]] = None,
        system_prompt: Optional[str] = None,
        top_n: int = 12,
        similarity_threshold: float = 0.1,
        vector_similarity_weight: float = 0.3,
        top_k: int = 5,
        enable_quote: bool = True,
        enable_multiturn_refine: bool = False,
        enable_multi_questions: bool = False,
        enable_keyword_extraction: bool = False,
        enable_deep_research: bool = False,
        enable_web_search: bool = False,
        use_kg: bool = False,
        target_language: Optional[str] = None,
        tavily_api_key: Optional[str] = None,
        temperature: float = 0.1,
        chat_model_provider: Optional[str] = None,
        chat_model_name: Optional[str] = None,
        is_stream: bool = False,
    ) -> AsyncGenerator[dict, None]:
        """
        统一问答入口：通过参数控制单轮/多轮、是否使用知识库、各类能力开关。
        - kb_ids 为空或 None：纯模型问答，不做检索。
        - kb_ids 有值：RAG 流程（可选 SQL、多问题、深度研究、网络搜索、知识图谱等）。
        """
        try:
            async for chunk in QAService.ask(
                session=session,
                tenant_id=tenant_id,
                user_id=user_id,
                messages=messages,
                kb_ids=kb_ids,
                doc_ids=doc_ids,
                system_prompt=system_prompt,
                top_n=top_n,
                similarity_threshold=similarity_threshold,
                vector_similarity_weight=vector_similarity_weight,
                top_k=top_k,
                enable_quote=enable_quote,
                enable_multiturn_refine=enable_multiturn_refine,
                enable_multi_questions=enable_multi_questions,
                enable_keyword_extraction=enable_keyword_extraction,
                enable_deep_research=enable_deep_research,
                enable_web_search=enable_web_search,
                use_kg=use_kg,
                target_language=target_language,
                tavily_api_key=tavily_api_key,
                temperature=temperature,
                chat_model_provider=chat_model_provider,
                chat_model_name=chat_model_name,
                is_stream=is_stream,
            ):
                yield chunk
        except Exception as e:
            logging.error(f"KBChatService.ask 执行失败: {e}")
            raise
