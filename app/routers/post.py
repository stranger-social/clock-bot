from typing import List, Optional

from app import oauth2
from .. import models, schemas, utils, oauth2
from fastapi import APIRouter, Body, FastAPI, HTTPException, Response, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)

@router.get("/", response_model=List[schemas.PostOut])
async def get_posts(db: Session = Depends(get_db), current_user: int = Depends (oauth2.get_current_user), limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    # posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()

    results = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    

    return results


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
async def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends (oauth2.get_current_user)):
    new_post = models.Post(owner_id=current_user.id , **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/latest", response_model=schemas.PostOut)
async def get_latest_post(db: Session = Depends(get_db), current_user: int = Depends (oauth2.get_current_user)):
    latest_post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).order_by(models.Post.id.desc()).first()
    return latest_post


@router.get("/{id}", response_model=schemas.PostOut)
async def get_post(id: int, response: Response, db: Session = Depends(get_db), current_user: int = Depends (oauth2.get_current_user)):
    
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Message with ID {str(id)} was not found")
    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int, response: Response, db: Session = Depends(get_db), current_user: int = Depends (oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Message with ID {str(id)} was not found")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not authorized to perform requested action")

    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.PostResponse)
async def update_post(id: int, updated_post: schemas.PostCreate, response: Response, db: Session = Depends(get_db), current_user: int = Depends (oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Message with ID {str(id)} was not found")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not authorized to perform requested action")
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()
