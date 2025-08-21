import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship

from .database import Base

class Conversation(Base):
    """
    对话会话的ORM模型，对应数据库中的 'conversations' 表。
    """
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True, comment="会话ID，主键")
    created_at = Column(DateTime, default=datetime.datetime.utcnow, comment="会话创建时间")

    # 'relationship' 定义了与Message模型的一对多关系。
    # 'back_populates' 指明了在Message模型中对应的反向关系属性。
    # 'cascade="all, delete-orphan"' 表示当一个Conversation被删除时，
    # 所有关联的Message也应被一并删除。
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    """
    消息的ORM模型，对应数据库中的 'messages' 表。
    """
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True, comment="消息ID，主键")
    conversation_id = Column(Integer, ForeignKey("conversations.id"), comment="所属会话的外键")

    content = Column(Text, nullable=False, comment="消息内容")

    # 消息类型，例如 'user' 或 'ai'
    message_type = Column(String(10), nullable=False, comment="消息类型（user 或 ai）")

    created_at = Column(DateTime, default=datetime.datetime.utcnow, comment="消息创建时间")

    # 'source_documents' 字段用于存储AI回答时引用的溯源文档。
    # 使用JSON类型可以方便地存储结构化数据。
    # SQLite原生支持JSON类型，但为了更好的跨数据库兼容性，有时也会用Text类型存储JSON字符串。
    source_documents = Column(JSON, nullable=True, comment="AI回答的溯源文档（JSON格式）")

    # 定义与Conversation模型的反向关系
    conversation = relationship("Conversation", back_populates="messages")
