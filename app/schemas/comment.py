from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from .user import UserResponse

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    post_id: int

class CommentUpdate(BaseModel):
    content: Optional[str] = None

class CommentResponse(CommentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    user_id: int
    post_id: int
    author: UserResponse
    
    class Config:
        from_attributes = True