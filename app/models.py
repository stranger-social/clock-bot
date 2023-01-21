from csv import unregister_dialect
from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship

from .database import Base

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, nullable=False)
    content = Column(String, nullable=False)
    sensitive = Column(Boolean, server_default="False", nullable=False)
    spoiler_text = Column(String, nullable=True)
    visibility = Column(String, nullable=False, default="unlisted")
    crontab_schedule = Column(String, nullable=False)
    next_run = Column(TIMESTAMP(timezone=False), nullable=True)
    published = Column(Boolean, server_default="True", nullable=False)
    created_at = Column(TIMESTAMP(timezone=False), nullable=False, server_default=text('now()'))
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    owner = relationship("User")
    bot_token_id = Column(Integer, ForeignKey("bot_tokens.id", ondelete="CASCADE"), nullable=True)
    bot_token = relationship("BotToken", back_populates="post")
    media_path = Column(String, nullable=True)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=False), nullable=False, server_default=text('now()'))    
    is_active = Column(Boolean, nullable=False, default=True)
    is_admin = Column(Boolean, nullable=False, default=False)

class PostLog(Base):
    __tablename__ = "post_log"

    id = Column(Integer, primary_key=True, nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    last_posted = Column(TIMESTAMP(timezone=False), nullable=False)
    post = relationship("Post")

class BotToken(Base):
    __tablename__ = "bot_tokens"

    id = Column(Integer, primary_key=True, nullable=False)
    token = Column(String, nullable=False)
    description = Column(String, nullable=True)
    post = relationship("Post", back_populates="bot_token")