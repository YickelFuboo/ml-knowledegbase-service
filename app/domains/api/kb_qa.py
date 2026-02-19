import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
import json
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database import get_db
from app.domains.schemes.kb_qa import KbQueryRequest, QaResponse
from app.domains.services.kb_qa_service import QAService

router = APIRouter(prefix="/qa", tags=["问答服务"])


@router.post("/kb-query", response_model=QaResponse)
async def kb_query(
    request: KbQueryRequest,
    user_id: str = Query(..., description="用户ID"),
    tenant_id: str = Query(..., description="租户ID"),
    db: AsyncSession = Depends(get_db)
):
    """知识库查询接口"""
    try:
        # 验证请求参数
        if not request.question.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "问题不能为空"}
            )
        
        if not request.kb_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "知识库ID列表不能为空"}
            )

        response_generator = QAService.kb_query(
            db=db,
            tenant_id=tenant_id,
            user_id=user_id,
            kb_ids=request.kb_ids,
            question=request.question,
            session_id=request.session_id,
            doc_ids=request.doc_ids,
            model_provider=request.model_provider,
            model_name=request.model_name,
            enable_quote=request.enable_quote,
            enable_multi_questions=request.enable_multi_questions,
            enable_keyword_extraction=request.enable_keyword_extraction,
            enable_deep_research=request.enable_deep_research,
            enable_web_search=request.enable_web_search,
            enable_knowledge_graph=request.enable_knowledge_graph,
            target_language=request.target_language,
            is_stream=False
        )

        # 获取最终结果
        final_response = None
        async for response in response_generator:
            final_response = response
        
        if not final_response:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"message": "知识库查询失败，未返回结果"}
            )

        return QaResponse(**final_response)
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"知识库查询失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"知识库查询失败: {str(e)}"}
        )


@router.post("/kb-query/stream")
async def kb_query_stream(
    request: KbQueryRequest,
    user_id: str = Query(..., description="用户ID"),
    tenant_id: str = Query(..., description="租户ID"),
    db: AsyncSession = Depends(get_db)
):
    """知识库查询流式接口"""
    try:
        # 验证请求参数
        if not request.question.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "问题不能为空"}
            )
        
        if not request.kb_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "知识库ID列表不能为空"}
            )

        response_generator = QAService.kb_query(
            db=db,
            tenant_id=tenant_id,
            user_id=user_id,
            kb_ids=request.kb_ids,
            question=request.question,
            session_id=request.session_id,
            doc_ids=request.doc_ids,
            model_provider=request.model_provider,
            model_name=request.model_name,
            enable_quote=request.enable_quote,
            enable_multi_questions=request.enable_multi_questions,
            enable_keyword_extraction=request.enable_keyword_extraction,
            enable_deep_research=request.enable_deep_research,
            enable_web_search=request.enable_web_search,
            enable_knowledge_graph=request.enable_knowledge_graph,
            target_language=request.target_language,
            is_stream=True
        )
        
        async def generate_stream():
            try:
                async for response in response_generator:
                    json_str = json.dumps(response, ensure_ascii=False)
                    yield f"data: {json_str}\n\n"
            except Exception as e:
                logging.error(f"流式知识库查询失败: {e}")
                error_response = {
                    "answer": f"抱歉，处理您的问题时出现了错误：{str(e)}",
                    "reference": {"total": 0, "chunks": [], "doc_aggs": []},
                    "prompt": "",
                    "created_at": None,
                    "session_id": None
                }
                json_str = json.dumps(error_response, ensure_ascii=False)
                yield f"data: {json_str}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain; charset=utf-8",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/plain; charset=utf-8"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"流式知识库查询失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"流式知识库查询失败: {str(e)}"}
        )
