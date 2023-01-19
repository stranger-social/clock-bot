from typing import List
from datetime import datetime, timedelta
from .. import models, schemas, utils, oauth2
from fastapi import APIRouter, Body, FastAPI, HTTPException, Response, status, Depends
from sqlalchemy.orm import Session
from ..database import get_db

router = APIRouter(
    prefix="/admin",
    tags=['Admin']
)

'''
Initialize first admin user
check database for existing admin user
if ANY admin user exists, return 403 Forbidden
if admin user does not exist, create admin user
'''
@router.post("/init", status_code=status.HTTP_201_CREATED, description="Initialize first admin user [can only be run once]")
def init_admin(
    response: Response,
    db: Session = Depends(get_db),
    user: schemas.UserCreate = Body(...)
):
    # check if database exists
    
    if utils.check_admin(db):
        response.status_code = status.HTTP_403_FORBIDDEN
        return {"message": "An admin user already exists"}
    else:
        utils.create_admin(db, user)
        response.status_code = status.HTTP_201_CREATED
        return {"message": "Admin user created"}


'''
create new user
must be logged in as admin user
if new user email exisists in database, return 403 Forbidden
if user does not exist in database, create user return 201 Created
make user is_active: true by default
'''
@router.post("/create_user", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse, description="Create new user [must be logged in as admin user]")
def create_user(
    db: Session = Depends(get_db),
    user: schemas.UserCreate = Body(...),
    current_user: int = Depends(oauth2.get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Admin user required")
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User already exists")
    else:
        hashed_password = utils.hash(user.password)
        user.password = hashed_password
        new_user = models.User(**user.dict())
        db.add(new_user)
        db.commit()
        return new_user


'''
get user by id
use schmeas.UserResponse to exclude password
current user must be admin user
'''
@router.get("/get_user/{id}", status_code=status.HTTP_200_OK, response_model=schemas.UserResponse, description="Get user by id [must be logged in as admin user]")
def get_user(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Admin user required")
    else:
        user = db.query(models.User).filter(models.User.id == id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"User with id {id} not found")
        else:
            return user


'''
get all users
use schmeas.UserResponse to exclude password
current user must be admin user
'''
@router.get("/get_users", status_code=status.HTTP_200_OK, response_model=List[schemas.UserResponse], description="Get all users [must be logged in as admin user]")
def get_users(
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Admin user required")
    else:
        users = db.query(models.User).all()
        if not users:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"No users found")
        else:
            return users


'''
toggle user active status
use schmeas.UserResponse to exclude password
current user must be admin user
cannot toggle is_active of self
'''
@router.put("/toggle_active/{id}", status_code=status.HTTP_200_OK, response_model=schemas.UserResponse, description="Toggle user active status [must be logged in as admin user]")
def toggle_active(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Admin user required")
    else:
        user = db.query(models.User).filter(models.User.id == id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"User with id {id} not found")
        else:
            if current_user.id == id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail=f"Cannot toggle is_active on self")
            else:
                if user.is_active == True:
                    user.is_active = False
                else:
                    user.is_active = True
                db.commit()
                db.refresh(user)
                return user


'''
toggle user is_admin status
use schmeas.UserResponse to exclude password
current user must be admin user
cannot toggle is_admin of self
'''
@router.put("/toggle_admin/{id}", status_code=status.HTTP_200_OK, response_model=schemas.UserResponse, description="Toggle user is_admin status [must be logged in as admin user]")
def toggle_admin(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Admin user required")
    else:
        user = db.query(models.User).filter(models.User.id == id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"User with id {id} not found")
        else:
            if current_user.id == id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail=f"Cannot toggle is_admin on self")
            else:
                if user.is_admin == True:
                    user.is_admin = False
                else:
                    user.is_admin = True
                db.commit()
                db.refresh(user)
                return user

'''
delete user by id
current user must be admin user
current user must be active user
cannot delete self
'''
@router.delete("/delete_user/{id}", status_code=status.HTTP_200_OK, description="Delete user by id [must be logged in as admin user]")
def delete_user(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Admin user required")
    else:
        user = db.query(models.User).filter(models.User.id == id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"User with id {id} not found")
        else:
            if current_user.id == id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail=f"Cannot delete self")
            else:
                db.delete(user)
                db.commit()
                return {"message": f"User with id {id} deleted"}


'''
generate permenant token for user by id
current user must be admin user
'''
@router.get("/generate_token/{id}", status_code=status.HTTP_200_OK, response_model=schemas.ApiToken, description="Generate permenant token for user by id [must be logged in as admin user]")
def generate_token(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Admin user required")
    else:
        user = db.query(models.User).filter(models.User.id == id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"User with id {id} not found")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"User is not active")                        
        else:
            access_token = oauth2.create_api_token(data = {"user_id": id})
            return {"user_id": id, "access_token": access_token, "token_type": "bearer"}
