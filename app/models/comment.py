from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from ..database import Base

class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True, onupdate=text('CURRENT_TIMESTAMP'))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    
    author = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")