from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, utils
from ..schemas.user import UserCreate, UserResponse, UserDetail
from ..database import get_db
from typing import List
from ..utils.auth import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Hash the password
    hashed_password = utils.get_password_hash(user.password)
    user.password = hashed_password
    
    # Check if email already exists
    email_exists = db.query(models.User).filter(models.User.email == user.email).first()
    if email_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    # Check if username already exists
    username_exists = db.query(models.User).filter(models.User.username == user.username).first()
    if username_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
    
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.get("/{id}", response_model=schemas.UserDetail)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {id} not found")
    
    post_count = db.query(models.Post).filter(models.Post.user_id == id).count()
    user_dict = user.__dict__.copy()
    user_dict["post_count"] = post_count
    
    return user_dict

@router.get("/", response_model=List[schemas.UserResponse])
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users

@router.put("/{id}", response_model=schemas.UserResponse)
def update_user(id: int, updated_user: schemas.UserUpdate, db: Session = Depends(get_db), 
                current_user: models.User = Depends(get_current_user)):
    user_query = db.query(models.User).filter(models.User.id == id)
    user = user_query.first()
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {id} not found")
    
    if user.id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    update_data = updated_user.dict(exclude_unset=True)
    user_query.update(update_data, synchronize_session=False)
    db.commit()
    db.refresh(user)
    
    return user