import datetime
from pydantic import BaseModel, Field
from typing import List

from .message import Message

class Conversation(BaseModel):
    """
    Represents a full conversation with its messages for API responses.
    """
    id: int
    created_at: datetime.datetime
    messages: List[Message] = Field(default_factory=list, description="The list of messages in this conversation")

    class Config:
        """
        Pydantic configuration to allow creating the model from ORM objects.
        """
        orm_mode = True

class ConversationSnippet(BaseModel):
    """
    Represents a snippet of a conversation, used for listing all conversations.
    It includes the ID and the first message to give a preview.
    """
    id: int
    created_at: datetime.datetime
    title: str = Field(description="A title for the conversation, usually the first user message.")

    class Config:
        orm_mode = True
