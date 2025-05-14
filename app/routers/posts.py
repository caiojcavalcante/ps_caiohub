from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from app.schemas.post import PostResponse
from app.api.auth import get_db
from typing import List, Optional
from ..utils.auth import get_current_user
from sqlalchemy import func
from ..models import user

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

@router.get("/", response_model=List[PostResponse])
def get_posts(db: Session = Depends(get_db), current_user: models.user = Depends(get_current_user),
              limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    
    posts = db.query(models.Post, 
                    func.count(models.Like.post_id).label("like_count"),
                    func.count(models.Comment.post_id).label("comment_count"))\
              .join(models.user, models.Post.user_id == models.user.id, isouter=True)\
              .join(models.Like, models.Like.post_id == models.Post.id, isouter=True)\
              .join(models.Comment, models.Comment.post_id == models.Post.id, isouter=True)\
              .filter(models.Post.content.contains(search))\
              .group_by(models.Post.id, models.user.id)\
              .order_by(models.Post.created_at.desc())\
              .limit(limit)\
              .offset(skip)\
              .all()
    
    results = []
    for post, like_count, comment_count in posts:
        liked_by_user = db.query(models.Like).filter(
            models.Like.post_id == post.id, 
            models.Like.user_id == current_user.id
        ).first() is not None
        
        post_dict = {**post.__dict__}
        post_dict["like_count"] = like_count
        post_dict["comment_count"] = comment_count
        post_dict["liked_by_user"] = liked_by_user
        results.append(post_dict)
    
    return results

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), 
                current_user: models.user = Depends(get_current_user)):
    new_post = models.Post(user_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    post_with_author = db.query(models.Post, 
                              func.count(models.Like.post_id).label("like_count"),
                              func.count(models.Comment.post_id).label("comment_count"))\
                          .join(models.user, models.Post.user_id == models.user.id)\
                          .outerjoin(models.Like, models.Like.post_id == models.Post.id)\
                          .outerjoin(models.Comment, models.Comment.post_id == models.Post.id)\
                          .filter(models.Post.id == new_post.id)\
                          .group_by(models.Post.id, models.user.id)\
                          .first()
    
    post, like_count, comment_count = post_with_author
    post_dict = {**post.__dict__}
    post_dict["like_count"] = like_count
    post_dict["comment_count"] = comment_count
    post_dict["liked_by_user"] = False
    
    return post_dict

@router.get("/{id}", response_model=schemas.PostResponse)
def get_post(id: int, db: Session = Depends(get_db), current_user: models.user = Depends(get_current_user)):
    post_query = db.query(models.Post, 
                        func.count(models.Like.post_id).label("like_count"),
                        func.count(models.Comment.post_id).label("comment_count"))\
                   .join(models.user, models.Post.user_id == models.user.id)\
                   .outerjoin(models.Like, models.Like.post_id == models.Post.id)\
                   .outerjoin(models.Comment, models.Comment.post_id == models.Post.id)\
                   .filter(models.Post.id == id)\
                   .group_by(models.Post.id, models.user.id)
    
    post_result = post_query.first()
    
    if not post_result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {id} not found")
    
    post, like_count, comment_count = post_result
    liked_by_user = db.query(models.Like).filter(
        models.Like.post_id == post.id, 
        models.Like.user_id == current_user.id
    ).first() is not None
    
    post_dict = {**post.__dict__}
    post_dict["like_count"] = like_count
    post_dict["comment_count"] = comment_count
    post_dict["liked_by_user"] = liked_by_user
    
    return post_dict

@router.put("/{id}", response_model=schemas.PostResponse)
def update_post(id: int, updated_post: schemas.PostUpdate, db: Session = Depends(get_db), 
                current_user: models.user = Depends(get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {id} not found")
    
    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    update_data = updated_post.dict(exclude_unset=True)
    post_query.update(update_data, synchronize_session=False)
    db.commit()
    db.refresh(post)
    
    # Get post with counts
    post_with_counts = db.query(models.Post, 
                              func.count(models.Like.post_id).label("like_count"),
                              func.count(models.Comment.post_id).label("comment_count"))\
                          .join(models.user, models.Post.user_id == models.user.id)\
                          .outerjoin(models.Like, models.Like.post_id == models.Post.id)\
                          .outerjoin(models.Comment, models.Comment.post_id == models.Post.id)\
                          .filter(models.Post.id == id)\
                          .group_by(models.Post.id, models.user.id)\
                          .first()
    
    post, like_count, comment_count = post_with_counts
    liked_by_user = db.query(models.Like).filter(
        models.Like.post_id == post.id, 
        models.Like.user_id == current_user.id
    ).first() is not None
    
    post_dict = {**post.__dict__}
    post_dict["like_count"] = like_count
    post_dict["comment_count"] = comment_count
    post_dict["liked_by_user"] = liked_by_user
    
    return post_dict

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: models.user = Depends(get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {id} not found")
    
    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    post_query.delete(synchronize_session=False)
    db.commit()
    
    return

@router.post("/{id}/like", status_code=status.HTTP_201_CREATED)
def like_post(id: int, db: Session = Depends(get_db), current_user: models.user = Depends(get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {id} not found")
    
    like_query = db.query(models.Like).filter(
        models.Like.post_id == id, 
        models.Like.user_id == current_user.id
    )
    found_like = like_query.first()
    
    if found_like:
        # If already liked, remove the like
        like_query.delete(synchronize_session=False)
        db.commit()
        return {"message": "Post unliked"}
    else:
        # Create a new like
        new_like = models.Like(post_id=id, user_id=current_user.id)
        db.add(new_like)
        db.commit()
        return {"message": "Post liked"}