import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from app.domains.schemes.llm_chat import ChatRequest, ChatResponse
from app.domains.services.llm_chat_service import chat_process


router = APIRouter(prefix="/chat", tags=["聊天服务"])


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """聊天接口（非流式）"""
    try:
        final_response = None
        async for response in chat_process(
            session_id=request.session_id,
            user_question=request.user_question,
            user_id=request.user_id,
            model_provider=request.model_provider,
            model_name=request.model_name,
            enable_web_search=request.enable_web_search,
            metadata=request.metadata,
            is_stream=False,
        ):
            final_response = response
        if not final_response:
            raise HTTPException(status_code=500, detail="聊天未返回结果")
        return ChatResponse(
            session_id=final_response["session_id"],
            content=final_response["content"],
            token_count=final_response.get("token_count"),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream", response_class=StreamingResponse)
async def stream_chat(request: ChatRequest):
    """流式聊天接口。服务侧与 POST / 共用同一 chat 生成器，仅 is_stream=True。"""
    try:
        async def generate():
            async for item in chat_process(
                session_id=request.session_id,
                user_question=request.user_question,
                user_id=request.user_id,
                model_provider=request.model_provider,
                model_name=request.model_name,
                enable_web_search=request.enable_web_search,
                metadata=request.metadata,
                is_stream=True,
            ):
                yield f"data: {json.dumps(item)}\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test-stream", response_class=HTMLResponse)
async def test_stream_page():
    """测试流式响应的HTML页面"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Stream Chat Test</title>
        <style>
            #chat-box {
                width: 80%;
                height: 400px;
                border: 1px solid #ccc;
                margin: 20px auto;
                padding: 10px;
                overflow-y: auto;
                white-space: pre-wrap;
            }
            #input-box {
                width: 80%;
                margin: 0 auto;
                display: flex;
                gap: 10px;
            }
            #question {
                flex-grow: 1;
                padding: 5px;
            }
        </style>
    </head>
    <body>
        <div id="chat-box"></div>
        <div id="input-box">
            <input type="text" id="question" placeholder="输入问题...">
            <button onclick="sendMessage()">发送</button>
        </div>

        <script>
            // 获取当前域名和端口
            const baseUrl = window.location.origin;
            
            async function sendMessage() {
                const question = document.getElementById('question').value;
                if (!question) return;
                
                const chatBox = document.getElementById('chat-box');
                chatBox.innerHTML += `\\n我: ${question}\\n`;
                document.getElementById('question').value = '';

                try {
                    const response = await fetch(`${baseUrl}/api/v1/chat/stream`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            user_question: question,
                            user_id: 'anonymous',
                            model_provider: null,
                            model_name: null
                        })
                    });

                    const reader = response.body.getReader();
                    const decoder = new TextDecoder();
                    let buffer = '';
                    chatBox.innerHTML += '助手: ';
                    while (true) {
                        const {value, done} = await reader.read();
                        if (done) break;
                        buffer += decoder.decode(value, {stream: true});
                        const lines = buffer.split('\\n\\n');
                        buffer = lines.pop() || '';
                        for (const line of lines) {
                            if (line.startsWith('data: ')) {
                                try {
                                    const data = JSON.parse(line.slice(6));
                                    if (data.session_id) {
                                        window._lastSessionId = data.session_id;
                                    }
                                    if (data.content !== undefined) {
                                        chatBox.innerHTML += data.content;
                                        chatBox.scrollTop = chatBox.scrollHeight;
                                    }
                                } catch (e) {}
                            }
                        }
                    }
                    chatBox.innerHTML += '\\n';
                } catch (error) {
                    console.error('Error:', error);
                    chatBox.innerHTML += `错误: ${error.message}\\n`;
                }
            }

            // 支持回车发送
            document.getElementById('question').addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
        </script>
    </body>
    </html>
    """
    return html
