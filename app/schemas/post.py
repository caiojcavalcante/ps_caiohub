from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from .user import UserResponse

class PostBase(BaseModel):
    content: str
    image_url: Optional[str] = None

class PostCreate(PostBase):
    pass

class PostUpdate(PostBase):
    content: Optional[str] = None
    image_url: Optional[str] = None

class PostResponse(PostBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    user_id: int
    author: UserResponse
    like_count: int
    comment_count: int
    liked_by_user: bool = False
    
    class Config:
        from_attributes = True