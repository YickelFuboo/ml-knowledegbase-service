import logging
from typing import Optional, AsyncGenerator, Dict, Any, List

from app.infrastructure.llms import llm_factory
from app.infrastructure.web_search.tavily import Tavily
from app.agent_frame.session.message import Message
from app.agent_frame.session.manager import session_manager


SYSTEM_PROMPT = "你是AI助手Pando，请根据用户的问题，给出详细的回答。"

SYSTEM_PROMPT_WITH_THINK = """你是AI助手Pando，请根据用户的问题，给出详细的回答。
你首先需要思考如何解决这个问题，然后根据你的思考来设计解决方案。要求：
1. 请在<thinking></thinking>标签中呈现你的分析过程，评估你已经拥有哪些信息，以及你需要哪些信息来继续完成任务。
2. 请确保<thinking></thinking>标签中内容在响应消息的开头部分。"""

WEB_SEARCH_PROMPT_PREFIX = "\n\n以下为联网检索到的参考信息，请结合这些信息回答用户问题：\n"


async def chat_process(
    session_id: Optional[str],
    user_question: str,
    user_id: str = "anonymous",
    model_provider: Optional[str] = None,
    model_name: Optional[str] = None,
    enable_web_search: bool = False,
    metadata: Optional[Dict[str, Any]] = None,
    is_stream: bool = False,
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    聊天统一入口，不区分流式/非流式，由 is_stream 控制生成行为。
    每次 yield 的 dict 形如: {"session_id": str, "content": str, "token_count": Optional[int]}。
    非流式时只 yield 一次；流式时先 yield session_id（content 为空），再逐 chunk yield，最后 yield token_count。
    """
    session = None
    if session_id:
        session = await session_manager.get_session(session_id)

    if not session:
        session_id = await session_manager.create_session(
            session_type="chat",
            user_id=user_id,
            description=user_question[:100] if user_question else "",
            metadata=metadata,
            llm_name=model_provider+"-"+model_name,
        )
        session = await session_manager.get_session(session_id)
        if not session:
            raise RuntimeError("创建会话失败")
    else:
        # 如果会话描述为空，则更新描述
        if not session.description:
            session.description = user_question[:100]
        # 如果会话存在，则更新模型，防止用户切换模型
        session.llm_name = model_provider+"-"+model_name


    history = [{"role": m.role.value, "content": m.content or ""} for m in session.get_history_for_context()]
    await session_manager.add_message(session_id, Message.user_message(user_question))

    system_prompt = SYSTEM_PROMPT
    if enable_web_search:
        try:
            tav = Tavily()
            tav_res = await tav.retrieve_chunks(user_question)
            if tav_res and tav_res.get("chunks"):
                parts = []
                for c in tav_res["chunks"]:
                    title = c.get("docnm_kwd") or ""
                    url = c.get("url") or ""
                    content = (c.get("content_with_weight") or "").strip()
                    if content:
                        parts.append(f"[{title}]({url})\n{content}")
                if parts:
                    system_prompt += WEB_SEARCH_PROMPT_PREFIX + "\n\n------\n\n".join(parts)
        except Exception as e:
            logging.warning(f"Tavily外部知识源检索失败: {e}")

    model = llm_factory.create_model(model_provider, model_name)
    if not model:
        raise ValueError(f"无法创建模型: provider={model_provider}, model_name={model_name}")

    if is_stream:
        yield {"session_id": session_id, "content": "", "token_count": None}
        stream_gen, token_count = await model.chat_stream(
            system_prompt=system_prompt,
            user_prompt="",
            user_question=user_question,
            history=history,
        )
        full: List[str] = []
        async for chunk in stream_gen:
            full.append(chunk)
            yield {"session_id": session_id, "content": chunk, "token_count": None}
        await session_manager.add_message(session_id, Message.assistant_message("".join(full)))
        yield {"session_id": session_id, "content": "", "token_count": token_count}
    else:
        response, token_count = await model.chat(
            system_prompt=system_prompt,
            user_prompt="",
            user_question=user_question,
            history=history,
        )
        content = response.content if hasattr(response, "content") else str(response)
        await session_manager.add_message(session_id, Message.assistant_message(content))
        yield {"session_id": session_id, "content": content, "token_count": token_count}
