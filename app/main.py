from fastapi import FastAPI
from app.database import engine
from app.models import user, post, comment
from app.api import users, auth
from app.routers import posts

# Cria tabelas
user.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Incluir as rotas do usuário
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(posts.router)