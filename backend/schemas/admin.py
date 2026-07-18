from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from backend.database.models import UserRole

class UserBase(BaseModel):
    username: str = Field(..., description="Username")
    role: UserRole = Field(default=UserRole.RECRUITER, description="User role")

class UserCreate(UserBase):
    password: str = Field(..., description="Plain password")

class UserUpdate(BaseModel):
    role: Optional[UserRole] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
