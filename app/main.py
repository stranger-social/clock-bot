import sys

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import engine
from .routers import post, admin, auth, bot
from .config import settings
from app import clock_bot

import logging

# Set logging level to variable settings.logging_level
logging.basicConfig(level=settings.logging_level)
logger = logging.getLogger(__name__)

# Configure the logger
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s"))
logger.addHandler(handler)

description = """
The clock-bot is a Mastodon bot that schedules repeating posts based on cron expressions.
"""

app = FastAPI(
    title="clock-bot",
    description=description,
    version="0.1.0",
    contact={
        "name": "azcoigreach",
        "url": "https://strangerproduction.com",
        "email": "azcoigreach@strangerproduction.com",
    },
    docs_url="/docs", redoc_url=None,
)

origins = ["*"] # Configured for public API

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(bot.router)
app.include_router(post.router)
app.include_router(admin.router)
app.include_router(auth.router)

@app.on_event("startup")
async def startup_event():
    pass

@app.get("/")
async def root():
    return {"message": "clock-bot API"}