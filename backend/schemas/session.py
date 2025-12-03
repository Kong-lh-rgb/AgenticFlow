from pydantic import BaseModel

class SessionCreateReq(BaseModel):
    title: str | None = None
