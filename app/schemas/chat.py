from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    """
    Represents the request body for the main chat endpoint.
    """
    question: str = Field(..., description="The user's question.", min_length=1)
    conversation_id: Optional[int] = Field(None, description="The ID of the existing conversation to continue.")

class StreamingChatResponse(BaseModel):
    """
    Represents a single chunk of a streaming chat response.
    """
    type: str # e.g., "stream", "sources", "end"
    data: Optional[str] = None # The token for "stream", or other data for other types
    sources: Optional[list] = None # The source documents for "sources" type
