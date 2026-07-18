from pydantic import BaseModel, ConfigDict, Field

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str = "student"

class TokenData(BaseModel):
    username: str | None = None
    role: str | None = None

class UserLogin(BaseModel):
    username: str = Field(..., description="User's login username")
    password: str = Field(..., description="User's plaintext password")
