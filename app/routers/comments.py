from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from typing import List
from ..utils.auth import get_current_user

router = APIRouter(
    prefix="/comments",
    tags=["Comments"]
)

@router.get("/post/{post_id}", response_model=List[schemas.CommentResponse])
def get_comments_for_post(post_id: int, db: Session = Depends(get_db), 
                        current_user: models.User = Depends(get_current_user)):
    # Check if post exists
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {post_id} not found")
    
    comments = db.query(models.Comment)\
                .filter(models.Comment.post_id == post_id)\
                .order_by(models.Comment.created_at.desc())\
                .all()
    
    return comments

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.CommentResponse)
def create_comment(comment: schemas.CommentCreate, db: Session = Depends(get_db), 
                   current_user: models.User = Depends(get_current_user)):
    # Check if post exists
    post = db.query(models.Post).filter(models.Post.id == comment.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {comment.post_id} not found")
    
    new_comment = models.Comment(user_id=current_user.id, **comment.dict())
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    
    return new_comment

@router.put("/{id}", response_model=schemas.CommentResponse)
def update_comment(id: int, updated_comment: schemas.CommentUpdate, db: Session = Depends(get_db), 
                   current_user: models.User = Depends(get_current_user)):
    comment_query = db.query(models.Comment).filter(models.Comment.id == id)
    comment = comment_query.first()
    
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Comment with id: {id} not found")
    
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    update_data = updated_comment.dict(exclude_unset=True)
    comment_query.update(update_data, synchronize_session=False)
    db.commit()
    db.refresh(comment)
    
    return comment

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    comment_query = db.query(models.Comment).filter(models.Comment.id == id)
    comment = comment_query.first()
    
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Comment with id: {id} not found")
    
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    comment_query.delete(synchronize_session=False)
    db.commit()
    
    return