import datetime
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class Message(BaseModel):
    """
    Represents a single message in a conversation for API responses.
    """
    id: int
    conversation_id: int
    content: str
    message_type: str = Field(..., description="Type of the message, e.g., 'user' or 'ai'")
    created_at: datetime.datetime
    source_documents: Optional[List[Dict[str, Any]]] = Field(None, description="List of source documents for AI messages")

    class Config:
        """
        Pydantic configuration to allow creating the model from ORM objects.
        """
        orm_mode = True
