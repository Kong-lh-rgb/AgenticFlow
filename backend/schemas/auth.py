from pydantic import BaseModel, Field

class RegisterReq(BaseModel):
    username: str = Field(min_length=2, max_length=64)
    password: str = Field(min_length=4, max_length=128)

class TokenResp(BaseModel):
    access_token: str
    token_type: str = "bearer"
