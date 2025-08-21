import datetime
from pydantic import BaseModel, Field
from typing import List

from .message import Message

class Conversation(BaseModel):
    """
    代表一个完整会话及其所有消息的Pydantic模型，用于API响应。
    """
    id: int
    created_at: datetime.datetime
    messages: List[Message] = Field(default_factory=list, description="该会话中的消息列表")

    class Config:
        """
        Pydantic配置，允许从ORM对象进行模型创建。
        """
        orm_mode = True

class ConversationSnippet(BaseModel):
    """
    代表一个会话的摘要信息，用于会话列表的API响应。
    它只包含ID、创建时间和由第一条消息生成的标题，用于前端的快速预览。
    """
    id: int
    created_at: datetime.datetime
    title: str = Field(description="会话标题，通常是第一条用户消息的摘要。")

    class Config:
        """
        Pydantic配置，允许从ORM对象进行模型创建。
        """
        orm_mode = True
