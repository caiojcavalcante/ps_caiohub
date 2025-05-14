from sqlalchemy.orm import Session
from app.models.post import Post
from app.schemas.post import PostCreate
from app.models.post import Post, Like
from app.models.comment import Comment
from fastapi import HTTPException

def create_post(db: Session, post_data: PostCreate, user_id: int):
    new_post = Post(
        content=post_data.content,
        image_url=post_data.image_url,
        user_id=user_id
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

def get_all_posts(db: Session):
    return db.query(Post).order_by(Post.created_at.desc()).all()

def get_user_posts(db: Session, user_id: int):
    return db.query(Post).filter(Post.user_id == user_id).order_by(Post.created_at.desc()).all()

def get_post_by_id(db: Session, post_id: int):
    return db.query(Post).filter(Post.id == post_id).first()

def update_post(db: Session, post_id: int, post_data: PostCreate):
    post_query = db.query(Post).filter(Post.id == post_id)
    post = post_query.first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post_query.update(post_data.dict(exclude_unset=True))
    db.commit()
    db.refresh(post)
    return post

def delete_post(db: Session, post_id: int):
    post_query = db.query(Post).filter(Post.id == post_id)
    post = post_query.first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post_query.delete()
    db.commit()
    return post

def like_post(db: Session, post_id: int, user_id: int):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    like = db.query(Like).filter(Like.post_id == post_id, Like.user_id == user_id).first()
    if like:
        db.delete(like)
        db.commit()
        return False  # Unliked
    else:
        new_like = Like(post_id=post_id, user_id=user_id)
        db.add(new_like)
        db.commit()
        return True  # Liked

def get_post_likes(db: Session, post_id: int):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    likes = db.query(Like).filter(Like.post_id == post_id).all()
    return [like.user_id for like in likes]

def get_post_like_count(db: Session, post_id: int):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    like_count = db.query(Like).filter(Like.post_id == post_id).count()
    return like_count


def get_post_comments(db: Session, post_id: int):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comments = db.query(Comment).filter(Comment.post_id == post_id).all()
    return comments
    
def get_post_comment_count(db: Session, post_id: int):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comment_count = db.query(Comment).filter(Comment.post_id == post_id).count()
    return comment_count
