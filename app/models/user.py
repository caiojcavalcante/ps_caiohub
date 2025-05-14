from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
from ..database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    username = Column(String, nullable=False, unique=True)
    bio = Column(String, nullable=True)
    profile_image = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    is_active = Column(Boolean, default=True)
    
    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="author")
    likes = relationship("Like", back_populates="user")
