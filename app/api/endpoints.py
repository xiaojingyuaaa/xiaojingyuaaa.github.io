from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List

from app.core.dependencies import get_db
from app.db import crud, models
from app.schemas import conversation as conv_schema
from app.schemas import message as msg_schema
from app.schemas import chat as chat_schema

router = APIRouter()

@router.post("/conversations/", response_model=conv_schema.Conversation, status_code=201)
def create_new_conversation(db: Session = Depends(get_db)):
    """
    Create a new, empty conversation.
    """
    new_conv = crud.create_conversation(db)
    # Manually create a title for the ConversationSnippet response
    # Since it's a new conversation, we can return a default or empty one.
    # The actual schema for this endpoint is Conversation, which doesn't have a title.
    # Let's adjust the response model to be more accurate.
    # The full conversation object is more useful here.
    return crud.get_conversation(db, new_conv.id)


@router.get("/conversations/", response_model=List[conv_schema.ConversationSnippet])
def get_all_conversations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get a list of all conversations.
    Returns a snippet of each conversation for preview.
    """
    conversations = crud.get_conversations(db, skip=skip, limit=limit)
    snippets = []
    for conv in conversations:
        first_message = conv.messages[0].content if conv.messages else "New Conversation"
        snippets.append(
            conv_schema.ConversationSnippet(
                id=conv.id,
                created_at=conv.created_at,
                title=first_message[:50] # Truncate title
            )
        )
    return snippets

@router.get("/conversations/{conversation_id}", response_model=conv_schema.Conversation)
def get_conversation_by_id(conversation_id: int, db: Session = Depends(get_db)):
    """
    Get the full details and message history of a specific conversation.
    """
    db_conversation = crud.get_conversation(db, conversation_id)
    if db_conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return db_conversation

@router.delete("/conversations/{conversation_id}", status_code=204)
def delete_a_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """
    Delete a conversation and all its messages.
    """
    db_conversation = crud.delete_conversation(db, conversation_id)
    if db_conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"ok": True} # Status code 204 means no content, so this isn't sent.


# This needs to be imported for the streaming response
from fastapi.responses import StreamingResponse
import json
from typing import AsyncGenerator, Dict, Any

from app.rag.chain import get_rag_chain

async def stream_chat_response_generator(
    conversation_id: int,
    user_question: str,
    db: Session
) -> AsyncGenerator[str, None]:
    """
    A generator function that streams the chat response.
    It yields JSON strings for different event types (token, sources, end).
    """
    # 1. Get RAG chain
    rag_chain = get_rag_chain()
    if not rag_chain:
        error_message = json.dumps({
            "type": "error",
            "data": "RAG chain not available."
        })
        yield f"data: {error_message}\n\n"
        return

    # 2. Retrieve chat history
    chat_history = []
    db_messages = crud.get_messages_by_conversation(db, conversation_id)
    for msg in db_messages:
        if msg.message_type == 'user':
            chat_history.append(("user", msg.content))
        else:
            chat_history.append(("ai", msg.content))

    # 3. Stream the response from the RAG chain
    full_ai_response = ""
    source_documents = []

    try:
        async for chunk in rag_chain.astream({
            "question": user_question,
            "chat_history": chat_history
        }):
            if "answer" in chunk:
                token = chunk["answer"]
                full_ai_response += token
                response_json = json.dumps({"type": "stream", "data": token})
                yield f"data: {response_json}\n\n"

            if "source_documents" in chunk and chunk["source_documents"]:
                source_documents = [doc.dict() for doc in chunk["source_documents"]]
                response_json = json.dumps({"type": "sources", "sources": source_documents})
                yield f"data: {response_json}\n\n"

    except Exception as e:
        error_message = json.dumps({
            "type": "error",
            "data": f"An error occurred during streaming: {str(e)}"
        })
        yield f"data: {error_message}\n\n"
        return

    # 4. Save the full AI response to the database
    if full_ai_response:
        crud.create_message(
            db,
            conversation_id=conversation_id,
            content=full_ai_response,
            message_type='ai',
            source_documents=source_documents
        )

    # 5. Signal the end of the stream
    end_message = json.dumps({"type": "end"})
    yield f"data: {end_message}\n\n"


@router.post("/chat/stream")
async def stream_chat(
    chat_request: chat_schema.ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Main endpoint for streaming chat responses.
    Handles conversation creation, message saving, and streaming the AI response.
    """
    conversation_id = chat_request.conversation_id

    # If no conversation_id is provided, create a new one
    if conversation_id is None:
        new_conv = crud.create_conversation(db)
        conversation_id = new_conv.id

    # Save the user's message
    crud.create_message(
        db,
        conversation_id=conversation_id,
        content=chat_request.question,
        message_type='user'
    )

    # Create the streaming response
    return StreamingResponse(
        stream_chat_response_generator(conversation_id, chat_request.question, db),
        media_type="text/event-stream"
    )
