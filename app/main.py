import sys

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import engine
from .routers import post, admin, auth, bot, list
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
This bot will allow you to schedule on a repeating schedule, discreetly to multiple Mastodon accounts.
Media files can be added to the post, and the bot will automatically upload the media to the Mastodon instance.

This bot is intended to be controlled via an API and can be used in conjunction with the clock-bot openapi documentation.

Bot Controls: 
- /bot/start - Start the bot
- /bot/tokens - Tokens for bot accounts on Mastodon

Posts:
- /posts - Posts to be scheduled with cron expressions. Use commands in the post to add dynamic content. 
  - {{list_random: 1}} to randomly select an item from a list_id of 1.
  - {{list_static: 1,1}} to select the first item from a list_id of 1 and item_id of 1. When creating lists, item_id is a custom integer but must be unique.
  - {{dynamic: https://stranger.social/api/v1/instance, stats.user_count}} to get an API JSON response from a URL and select a key from the response.
- media_path is the path to the media file on the bot server. e.g. /usr/src/app/media/image.jpg


Lists:
- /lists - Lists to be used in posts.
- /lists/{list_id}/items - Items to be used in lists. Item_id is a custom integer but must be unique.

Admin:
- /admin/init - Initialize the admin user
- Admin users can create and delete bot accounts on the bot server. And add new bot tokens.
- Active users can operate the bot and create posts and lists.

"""

app = FastAPI(
    title="clock-bot",
    description=description,
    version="0.2.2",
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
app.include_router(list.router)
app.include_router(admin.router)
app.include_router(auth.router)

@app.on_event("startup")
async def startup_event(background_tasks: BackgroundTasks):
    # Start clock-bot
    logger.info("clock-bot started")
    await clock_bot.clear_next_run()
    background_tasks.add_task(clock_bot.clock_bot_main)

@app.get("/")
async def root():
    return {"message": "clock-bot API"}