from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from . import models

# CRUD: Create, Read, Update, Delete

# -----------------------------------------------------------------------------
# 会话 (Conversation) CRUD 操作
# -----------------------------------------------------------------------------

def create_conversation(db: Session) -> models.Conversation:
    """
    创建一个新的对话会话。

    Args:
        db (Session): 数据库会话对象。

    Returns:
        models.Conversation: 新创建的会话对象。
    """
    db_conversation = models.Conversation()
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation

def get_conversation(db: Session, conversation_id: int) -> Optional[models.Conversation]:
    """
    根据ID获取单个对话会话。

    Args:
        db (Session): 数据库会话对象。
        conversation_id (int): 会话的ID。

    Returns:
        Optional[models.Conversation]: 找到的会话对象，如果不存在则为None。
    """
    return db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()

def get_conversations(db: Session, skip: int = 0, limit: int = 100) -> List[models.Conversation]:
    """
    获取所有对话会话的列表，支持分页。

    Args:
        db (Session): 数据库会话对象。
        skip (int): 跳过的记录数。
        limit (int): 返回的最大记录数。

    Returns:
        List[models.Conversation]: 会话对象列表。
    """
    return db.query(models.Conversation).order_by(models.Conversation.created_at.desc()).offset(skip).limit(limit).all()

def delete_conversation(db: Session, conversation_id: int) -> Optional[models.Conversation]:
    """
    根据ID删除一个对话会话及其所有关联的消息。

    Args:
        db (Session): 数据库会话对象。
        conversation_id (int): 要删除的会话ID。

    Returns:
        Optional[models.Conversation]: 被删除的会话对象，如果不存在则为None。
    """
    db_conversation = get_conversation(db, conversation_id)
    if db_conversation:
        db.delete(db_conversation)
        db.commit()
    return db_conversation

# -----------------------------------------------------------------------------
# 消息 (Message) CRUD 操作
# -----------------------------------------------------------------------------

def create_message(
    db: Session,
    conversation_id: int,
    content: str,
    message_type: str,
    source_documents: Optional[List[Dict[str, Any]]] = None
) -> models.Message:
    """
    在指定的会话中创建一条新消息。

    Args:
        db (Session): 数据库会话对象。
        conversation_id (int): 消息所属的会话ID。
        content (str): 消息内容。
        message_type (str): 消息类型，应为 'user' 或 'ai'。
        source_documents (Optional[List[Dict[str, Any]]]): AI消息的溯源文档列表。

    Returns:
        models.Message: 新创建的消息对象。
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
    根据会话ID获取所有消息，按时间升序排列。

    Args:
        db (Session): 数据库会话对象。
        conversation_id (int): 会话的ID。

    Returns:
        List[models.Message]: 该会话的消息列表。
    """
    return db.query(models.Message).filter(models.Message.conversation_id == conversation_id).order_by(models.Message.created_at.asc()).all()
