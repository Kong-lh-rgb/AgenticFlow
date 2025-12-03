from pydantic import BaseModel, Field

class ChatSendReq(BaseModel):
    session_id: int
    content: str = Field(min_length=1)
