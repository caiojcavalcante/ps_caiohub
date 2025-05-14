from pydantic import BaseModel, EmailStr

# Dados para o login (entrada)
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Retorno do token (saída)
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# payload do token
class TokenData(BaseModel):
    user_id: int | None = None
