from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from . import models

# -----------------------------------------------------------------------------
# Conversation CRUD
# -----------------------------------------------------------------------------

def create_conversation(db: Session) -> models.Conversation:
    """
    Creates a new conversation.
    """
    db_conversation = models.Conversation()
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation

def get_conversation(db: Session, conversation_id: int) -> Optional[models.Conversation]:
    """
    Gets a single conversation by its ID.
    """
    return db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()

def get_conversations(db: Session, skip: int = 0, limit: int = 100) -> List[models.Conversation]:
    """
    Gets all conversations with pagination.
    """
    return db.query(models.Conversation).order_by(models.Conversation.created_at.desc()).offset(skip).limit(limit).all()

def delete_conversation(db: Session, conversation_id: int) -> Optional[models.Conversation]:
    """
    Deletes a conversation and its messages.
    """
    db_conversation = get_conversation(db, conversation_id)
    if db_conversation:
        db.delete(db_conversation)
        db.commit()
    return db_conversation

# -----------------------------------------------------------------------------
# Message CRUD
# -----------------------------------------------------------------------------

def create_message(
    db: Session,
    conversation_id: int,
    content: str,
    message_type: str,
    source_documents: Optional[List[Dict[str, Any]]] = None
) -> models.Message:
    """
    Creates a new message in a conversation.
    'message_type' should be 'user' or 'ai'.
    'source_documents' is a list of dicts for 'ai' messages.
    """
    db_message = models.Message(
        conversation_id=conversation_id,
        content=content,
        message_type=message_type,
        source_documents=source_documents
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_messages_by_conversation(db: Session, conversation_id: int) -> List[models.Message]:
    """
    Gets all messages for a given conversation, ordered by creation time.
    """
    return db.query(models.Message).filter(models.Message.conversation_id == conversation_id).order_by(models.Message.created_at.asc()).all()
