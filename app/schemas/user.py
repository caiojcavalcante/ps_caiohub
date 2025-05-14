from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username: str
    bio: str | None = None
    profile_image: str | None = None

#  Resposta completa (uso privado, ex: /me)
class UserOut(BaseModel):
    id: int
    email: EmailStr
    username: str
    bio: str | None
    profile_image: str | None
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True

# Resposta pública (para usar dentro de outros objetos)
class UserResponse(BaseModel):
    id: int
    username: str
    profile_image: str | None = None

    class Config:
        from_attributes = True
