from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ChatRequest(BaseModel):
    """
    代表主聊天接口的请求体（request body）的Pydantic模型。
    """
    question: str = Field(..., description="用户的提问。", min_length=1)
    conversation_id: Optional[int] = Field(None, description="可选的、用于继续现有对话的会话ID。")

class StreamingChatResponse(BaseModel):
    """
    代表流式聊天响应中单个数据块的Pydantic模型。
    这个模型主要用于文档和内部逻辑，实际的流式数据是JSON字符串。
    """
    type: str = Field(..., description="数据块的类型，例如 'stream', 'sources', 'end', 'error'")
    data: Optional[str] = Field(None, description="当type为'stream'时，这里是具体的token。当type为'error'时，这里是错误信息。")
    sources: Optional[List[Dict[str, Any]]] = Field(None, description="当type为'sources'时，这里是溯源文档列表。")
