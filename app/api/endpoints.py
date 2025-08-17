from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from fastapi.responses import StreamingResponse
import json
from typing import AsyncGenerator

from app.core.dependencies import get_db
from app.db import crud
from app.schemas import conversation as conv_schema
from app.schemas import chat as chat_schema
from app.rag.chain import get_rag_chain

# 创建一个API路由实例
router = APIRouter()

@router.post("/conversations/", response_model=conv_schema.Conversation, status_code=201, summary="创建一个新会话")
def create_new_conversation(db: Session = Depends(get_db)):
    """
    创建一个新的、空的对话会话。
    """
    new_conv = crud.create_conversation(db)
    # 返回完整的会话对象，即使它是空的
    return crud.get_conversation(db, new_conv.id)


@router.get("/conversations/", response_model=List[conv_schema.ConversationSnippet], summary="获取所有会话列表")
def get_all_conversations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    获取所有对话会话的列表。
    为每个会话返回一个摘要信息（ID，创建时间，标题）用于预览。
    """
    conversations = crud.get_conversations(db, skip=skip, limit=limit)
    snippets = []
    for conv in conversations:
        # 使用第一条消息作为标题，如果不存在则使用默认标题
        first_message = conv.messages[0].content if conv.messages else "新会话"
        snippets.append(
            conv_schema.ConversationSnippet(
                id=conv.id,
                created_at=conv.created_at,
                title=first_message[:50]  # 截断标题长度
            )
        )
    return snippets

@router.get("/conversations/{conversation_id}", response_model=conv_schema.Conversation, summary="获取特定会话")
def get_conversation_by_id(conversation_id: int, db: Session = Depends(get_db)):
    """
    获取一个指定ID的完整对话，包含所有消息历史。
    """
    db_conversation = crud.get_conversation(db, conversation_id)
    if db_conversation is None:
        raise HTTPException(status_code=404, detail="会话未找到")
    return db_conversation

@router.delete("/conversations/{conversation_id}", status_code=204, summary="删除特定会话")
def delete_a_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """
    删除一个指定的对话及其所有关联的消息。
    """
    db_conversation = crud.delete_conversation(db, conversation_id)
    if db_conversation is None:
        raise HTTPException(status_code=404, detail="会话未找到")
    # 状态码204表示无内容，因此不返回任何响应体
    return


async def stream_chat_response_generator(
    conversation_id: int,
    user_question: str,
    db: Session
) -> AsyncGenerator[str, None]:
    """
    一个异步生成器函数，用于流式传输聊天响应。
    它会产生多种事件类型的JSON字符串（例如：token流，源信息，结束信号）。
    """
    # 1. 获取RAG链实例
    rag_chain = get_rag_chain()
    if not rag_chain:
        error_message = json.dumps({
            "type": "error",
            "data": "RAG链不可用。"
        })
        yield f"data: {error_message}\n\n"
        return

    # 2. 从数据库检索聊天历史
    chat_history = []
    db_messages = crud.get_messages_by_conversation(db, conversation_id)
    for msg in db_messages:
        if msg.message_type == 'user':
            chat_history.append(("user", msg.content))
        else:
            chat_history.append(("ai", msg.content))

    # 3. 从RAG链流式获取响应
    full_ai_response = ""
    source_documents = []

    try:
        # 使用astream方法进行异步流式调用
        async for chunk in rag_chain.astream({
            "question": user_question,
            "chat_history": chat_history
        }):
            # 处理答案的token块
            if "answer" in chunk:
                token = chunk["answer"]
                full_ai_response += token
                response_json = json.dumps({"type": "stream", "data": token}, ensure_ascii=False)
                yield f"data: {response_json}\n\n"

            # 处理溯源文档块
            if "source_documents" in chunk and chunk["source_documents"]:
                # 转换Document对象为可序列化的字典
                source_documents = [doc.dict() for doc in chunk["source_documents"]]
                response_json = json.dumps({"type": "sources", "sources": source_documents}, ensure_ascii=False)
                yield f"data: {response_json}\n\n"

    except Exception as e:
        error_message = json.dumps({
            "type": "error",
            "data": f"流式处理过程中发生错误: {str(e)}"
        }, ensure_ascii=False)
        yield f"data: {error_message}\n\n"
        return

    # 4. 将完整的AI回答保存到数据库
    if full_ai_response:
        crud.create_message(
            db,
            conversation_id=conversation_id,
            content=full_ai_response,
            message_type='ai',
            source_documents=source_documents
        )

    # 5. 发送结束信号
    end_message = json.dumps({"type": "end"})
    yield f"data: {end_message}\n\n"


@router.post("/chat/stream", summary="流式聊天接口")
async def stream_chat(
    chat_request: chat_schema.ChatRequest,
    db: Session = Depends(get_db)
):
    """
    用于流式聊天响应的主接口。
    处理会话创建、消息保存，并流式传输AI的回答。
    """
    conversation_id = chat_request.conversation_id

    # 如果未提供conversation_id，则创建一个新的会话
    if conversation_id is None:
        new_conv = crud.create_conversation(db)
        conversation_id = new_conv.id

    # 保存用户的消息到数据库
    crud.create_message(
        db,
        conversation_id=conversation_id,
        content=chat_request.question,
        message_type='user'
    )

    # 创建并返回流式响应
    return StreamingResponse(
        stream_chat_response_generator(conversation_id, chat_request.question, db),
        media_type="text/event-stream"
    )
