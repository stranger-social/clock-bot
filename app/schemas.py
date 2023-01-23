from typing import Optional
from pydantic import BaseModel, EmailStr, conint
from datetime import datetime

class PostBase(BaseModel):
    content: str
    crontab_schedule: str = "*/5 * * * *"
    sensitive: bool = False
    spoiler_text: str = None
    visibility: str = "direct"
    published: bool = True
    bot_token_id: int = None
    media_path: str = None
    

class PostCreate(PostBase):
    pass

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    is_active: bool
    is_admin: bool

    class Config:
        orm_mode = True

class PostResponse(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    bot_token_id: Optional[int] = None
    media_path: Optional[str] = None
    owner: UserResponse

    class Config:
        orm_mode = True

class PostOut(BaseModel):
    Post: PostResponse

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None

class ApiToken(BaseModel):
    user_id: int
    access_token: str
    token_type: str

class BotTokenCreate(BaseModel):
    token: str
    description: str = None

class BotTokenResponse(BaseModel):
    id: int
    token: str
    description: str = None

    class Config:
        orm_mode = True

class BotTokenOut(BaseModel):
    BotToken: BotTokenResponse

    class Config:
        orm_mode = True

class ListBase(BaseModel):
    title: str

class ListCreate(ListBase):
    pass

class ListResponse(ListBase):
    id: int
    date_created: datetime
    date_updated: Optional[datetime]
    class Config:
        orm_mode = True

class ListOut(BaseModel):
    List: ListResponse

    class Config:
        orm_mode = True

class ListContentBase(BaseModel):
    item_id: int
    content: str

class ListContentCreate(ListContentBase):
    pass

class ListContentResponse(ListContentBase):
    id: int
    list_id: int
    date_added: datetime
    date_last_used: Optional[datetime]

    class Config:
        orm_mode = True

class ListContentOut(BaseModel):
    ListContent: ListContentResponse

    class Config:
        orm_mode = True



