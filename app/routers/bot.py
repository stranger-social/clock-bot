from typing import List, Optional

from app import oauth2, clock_bot
from .. import models, schemas, oauth2
from fastapi import APIRouter, HTTPException, Response, status, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from ..database import get_db

import logging
logger = logging.getLogger(__name__)

# Bot controls for the clock-bot
router = APIRouter(
    prefix="/bot",
    tags=['Bot Controls']
)

is_running = False

# Start the clock-bot
@router.post("/start", status_code=status.HTTP_200_OK, description="Start the clock-bot [bot does not run automatically on startup]")
async def start_clock_bot(
    background_tasks: BackgroundTasks,
    current_user: int = Depends(oauth2.get_current_user)
    ):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User {str(current_user.username)} is not active.")
    else:
        global is_running
        if not is_running:
            logger.info("clock-bot started")
            await clock_bot.clear_next_run()
            background_tasks.add_task(clock_bot.clock_bot_main)
            is_running = True
            return {"message": "clock-bot started"}
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"clock-bot is already running.")

#  Endpoints to get, create, get_by_id, update, and delete bot_tokens
@router.get("/tokens", response_model=List[schemas.BotTokenResponse], description="Get all bot tokens [must be logged in]")
async def get_bot_tokens(
    db: Session = Depends(get_db), current_user: int = Depends (oauth2.get_current_user), limit: int = 10, skip: int = 0, search: Optional[str] = ""
    ):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User {str(current_user.username)} is not active.")
    else:
        results = db.query(models.BotToken).filter(models.BotToken.description.contains(search)).limit(limit).all()
        return results

@router.post("/tokens", status_code=status.HTTP_201_CREATED, response_model=schemas.BotTokenResponse, description="Create a bot token [must be logged in]")
async def create_bot_token(token: schemas.BotTokenCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Admin user required")
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User {str(current_user.username)} is not active.")
    else:
        db_token = models.BotToken(**token.dict())
        db.add(db_token)
        db.commit()
        db.refresh(db_token)
        return db_token

@router.get("/tokens/{token_id}", response_model=schemas.BotTokenResponse, description="Get a bot token by id [must be logged in]")
async def get_bot_token_by_id(token_id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User {str(current_user.username)} is not active.")
    else:
        token = db.query(models.BotToken).filter(models.BotToken.id == token_id).first()
        if not token:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Token with id {token_id} not found")
        return token

@router.put("/tokens/{token_id}", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.BotTokenResponse, description="Update a bot token by id [must be logged in]")
async def update_bot_token(token_id: int, token: schemas.BotTokenCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Admin user required")
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User {str(current_user.username)} is not active.")
    else:
        db_token = db.query(models.BotToken).filter(models.BotToken.id == token_id).first()
        if not db_token:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Token with id {token_id} not found")
        db_token.description = token.description
        db_token.token = token.token
        db.commit()
        db.refresh(db_token)
        return db_token

@router.delete("/tokens/{token_id}", status_code=status.HTTP_204_NO_CONTENT, description="Delete a bot token by id [must be logged in]")
async def delete_bot_token(token_id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Admin user required")
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User {str(current_user.username)} is not active.")
    else:
        db_token = db.query(models.BotToken).filter(models.BotToken.id == token_id).first()
        if not db_token:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Token with id {token_id} not found")
        db.delete(db_token)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)

        