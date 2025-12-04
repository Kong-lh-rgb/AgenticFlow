from pydantic import BaseModel, Field

class ChatSendReq(BaseModel):
    session_id: int
    content: str
    new_run: bool = False
