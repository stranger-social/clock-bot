from typing import List, Optional

from app import oauth2
from .. import models, schemas, oauth2
from fastapi import APIRouter, HTTPException, Response, status, Depends
from sqlalchemy.orm import Session
from ..database import get_db

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)

@router.get("/", response_model=List[schemas.PostResponse], description="Get all posts (paginated) (searchable by content) [must be logged in]")
async def get_posts(db: Session = Depends(get_db), current_user: int = Depends (oauth2.get_current_user), limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User {str(current_user.username)} is not active.")
    else:
        results = db.query(models.Post).group_by(models.Post.id).filter(models.Post.content.contains(search)).limit(limit).offset(skip).all()
        return results


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse, description="Create new clock-bot post [must be logged in]")
async def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends (oauth2.get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User {str(current_user.username)} is not active.")
    else:
        new_post = models.Post(owner_id=current_user.id , **post.dict())
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return new_post


@router.get("/{id}", response_model=schemas.PostResponse, description="Get post by ID [must be logged in]")
async def get_post(id: int, response: Response, db: Session = Depends(get_db), current_user: int = Depends (oauth2.get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User {str(current_user.username)} is not active.")
    else:
        post = db.query(models.Post).group_by(models.Post.id).filter(models.Post.id == id).first()
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Message with ID {str(id)} was not found")
        return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, description="Delete post by ID [must be logged in]")
async def delete_post(id: int, response: Response, db: Session = Depends(get_db), current_user: int = Depends (oauth2.get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User {str(current_user.username)} is not active.")
    else:
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


@router.put("/{id}", response_model=schemas.PostResponse, description="Update post by ID [must be logged in]")
async def update_post(id: int, updated_post: schemas.PostCreate, response: Response, db: Session = Depends(get_db), current_user: int = Depends (oauth2.get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User {str(current_user.username)} is not active.")
    else:
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
