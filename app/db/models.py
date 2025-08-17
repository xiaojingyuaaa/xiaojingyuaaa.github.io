import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship

from .database import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # This creates a back-reference so we can access conversation.messages
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))

    content = Column(Text, nullable=False)

    # 'user' or 'ai'
    message_type = Column(String(10), nullable=False)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Storing source documents as a JSON string for AI messages
    # SQLite has a JSON type, but using Text provides more flexibility across different DBs.
    source_documents = Column(JSON, nullable=True)

    # This creates a back-reference so we can access message.conversation
    conversation = relationship("Conversation", back_populates="messages")
