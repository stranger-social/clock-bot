from typing import List, Optional

from app import oauth2
from .. import models, schemas, oauth2
from fastapi import APIRouter, HTTPException, Response, status, Depends
from sqlalchemy.orm import Session
from ..database import get_db

from datetime import datetime 

router = APIRouter(
    prefix="/lists",
    tags=['Lists']
)

''' LIST ENDPOINTS
****************************************************************************************    
'''

# Endpoints to get, create, get_by_id, update, and delete lists
@router.get("/", response_model=List[schemas.ListResponse], description="Get all lists (paginated) (searchable by title) [must be logged in]")
async def get_lists(db: Session = Depends(get_db), current_user: int = Depends (oauth2.get_current_user), limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User {str(current_user.username)} is not active.")
    else:
        results = db.query(models.List).group_by(models.List.id).filter(models.List.title.contains(search)).limit(limit).offset(skip).all()
        return results

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.ListResponse, description="Create new clock-bot list [must be logged in]")
async def create_lists(list: schemas.ListCreate, db: Session = Depends(get_db), current_user: int = Depends (oauth2.get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User {str(current_user.username)} is not active.")
    else:
        db_list = models.List(title=list.title)
        db.add(db_list)
        db.commit()
        db.refresh(db_list)
        return db_list

@router.get("/{id}", response_model=schemas.ListResponse, description="Get list by id [must be logged in]")
async def get_list_by_id(id: int, db: Session = Depends(get_db), current_user: int = Depends (oauth2.get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User {str(current_user.username)} is not active.")
    else:
        db_list = db.query(models.List).filter(models.List.id == id).first()
        if not db_list:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"List with ID {str(id)} was not found.")
        return db_list

@router.put("/{id}", response_model=schemas.ListResponse, description="Update list by id [must be logged in]")
async def update_list_by_id(id: int, list: schemas.ListCreate, db: Session = Depends(get_db), current_user: int = Depends (oauth2.get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User {str(current_user.username)} is not active.")
    else:
        db_list = db.query(models.List).filter(models.List.id == id).first()
        if not db_list:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"List with ID {str(id)} was not found.")
        db_list.title = list.title
        db_list.date_updated = datetime.now()
        db.commit()
        db.refresh(db_list)
        return db_list
        
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, description="Delete list by id [must be logged in]")
async def delete_list_by_id(id: int, db: Session = Depends(get_db), current_user: int = Depends (oauth2.get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User {str(current_user.username)} is not active.")
    else:
        db_list = db.query(models.List).filter(models.List.id == id).first()
        if not db_list:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"List with ID {str(id)} was not found.")
        db.delete(db_list)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)

''' LIST CONTENT ENDPOINTS
****************************************************************************************
'''

# Endpoints to get, create, get_by_id, update, and delete list items
@router.get("/{id}/items", response_model=List[schemas.ListContentResponse], description="Get all list items (paginated) (searchable by content) [must be logged in]")
async def get_list_items(id: int, db: Session = Depends(get_db), current_user: int = Depends (oauth2.get_current_user), limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User {str(current_user.username)} is not active.")
    else:
        results = db.query(models.ListContent).group_by(models.ListContent.id).filter(models.ListContent.list_id == id).filter(models.ListContent.content.contains(search)).limit(limit).offset(skip).all()
        return results

@router.post("/{id}/items", status_code=status.HTTP_201_CREATED, response_model=schemas.ListContentResponse, description="Create new list item [must be logged in]")
async def create_list_items(id: int, list_item: schemas.ListContentCreate, db: Session = Depends(get_db), current_user: int = Depends (oauth2.get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User {str(current_user.username)} is not active.")
    else:
        db_list_item = models.ListContent(content=list_item.content, item_id=list_item.item_id, list_id=id)
        # Check if list_id exists
        if not db.query(models.List).filter(models.List.id == id).first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"List with ID {str(id)} was not found.")
        # check if item_id is already in list with list_id
        if db.query(models.ListContent).filter(models.ListContent.item_id == list_item.item_id).filter(models.ListContent.list_id == id).first():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"Item with ID {str(list_item.item_id)} is already in list with ID {str(id)}.")
        else:
            db.add(db_list_item)
            db.commit()
            db.refresh(db_list_item)
            return db_list_item

@router.get("/{id}/items/{item_id}", response_model=schemas.ListContentResponse, description="Get list item by id [must be logged in]")
async def get_list_item_by_id(id: int, item_id: int, db: Session = Depends(get_db), current_user: int = Depends (oauth2.get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User {str(current_user.username)} is not active.")
    else:
        db_list_item = db.query(models.ListContent).filter(models.ListContent.item_id == item_id).first()
        if not db_list_item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"List item with ID {str(item_id)} was not found.")
        return db_list_item
        
@router.put("/{id}/items/{item_id}", response_model=schemas.ListContentResponse, description="Update list item by id [must be logged in]")
async def update_list_item_by_id(id: int, item_id: int, list_item: schemas.ListContentCreate, db: Session = Depends(get_db), current_user: int = Depends (oauth2.get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User {str(current_user.username)} is not active.")
    else:
        # query item_id and list_id
        db_list_item = db.query(models.ListContent).filter(models.ListContent.item_id == item_id).filter(models.ListContent.list_id == id).first()
        if not db_list_item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"List item with ID {str(item_id)} was not found.")
        db_list_item.content = list_item.content
        db_list_item.item_id = list_item.item_id
        db.commit()
        db.refresh(db_list_item)
        return db_list_item
        
@router.delete("/{id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, description="Delete list item by id [must be logged in]")
async def delete_list_item_by_id(id: int, item_id: int, db: Session = Depends(get_db), current_user: int = Depends (oauth2.get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User {str(current_user.username)} is not active.")
    else:
        db_list_item = db.query(models.ListContent).filter(models.ListContent.item_id == item_id).filter(models.ListContent.list_id == id).first()
        if not db_list_item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"List item with ID {str(item_id)} was not found.")
        db.delete(db_list_item)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)

