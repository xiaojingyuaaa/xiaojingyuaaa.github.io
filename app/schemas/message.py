import datetime
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class Message(BaseModel):
    """
    代表会话中单条消息的Pydantic模型，用于API响应。
    """
    id: int
    conversation_id: int
    content: str
    message_type: str = Field(..., description="消息类型，例如 'user' 或 'ai'")
    created_at: datetime.datetime
    source_documents: Optional[List[Dict[str, Any]]] = Field(None, description="AI消息的溯源文档列表")

    class Config:
        """
        Pydantic的配置类。
        orm_mode = True 允许模型直接从ORM对象（如SQLAlchemy模型实例）创建，
        实现数据对象和API模型之间的自动映射。
        """
        orm_mode = True
