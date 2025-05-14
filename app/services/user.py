from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password

def create_user(db: Session, user_data: UserCreate):
    db_user = User(
        email=user_data.email,
        password=hash_password(user_data.password),  # << aqui faz hash da senha
        username=user_data.username,
        bio=user_data.bio,
        profile_image=user_data.profile_image
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user