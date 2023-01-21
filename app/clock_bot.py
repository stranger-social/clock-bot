import os 

from .config import settings
from .database import get_db
from . import models, schemas

from datetime import datetime
from fastapi import Depends
import asyncio
import aiohttp
import json
import croniter
import magic

import logging

logger = logging.getLogger(__name__)

'''
Main clock-bot logic
'''

def quiet_mode():
    if settings.quiet == True:
        logger.warning("quiet_mode: Quiet mode is enabled")
        return True
    else:
        return False


async def check_scheduled_posts():
    with get_db() as db:
        try:
            logger.debug("check_scheduled_posts: Checking scheduled posts")
            scheduled_posts = await get_scheduled_posts(db)
            for post in scheduled_posts:
                if await check_next_run(post):
                    await post_status(post)
                    
        except Exception as e:
            logger.error(f"check_scheduled_posts: {e}")

async def get_scheduled_posts(db):
    try:
        scheduled_posts = db.query(models.Post).filter(models.Post.published == True).all()
        scheduled_posts_count = len(scheduled_posts)
        logger.debug(f"get_scheduled_posts: scheduled_posts_count: {scheduled_posts_count}")        
        return scheduled_posts
    except Exception as e:
        logger.error(f"get_scheduled_posts: {e}")

async def check_next_run(post):
    try:
        current_time=datetime.now()
        if post.next_run == None:
            logger.debug(f"check_next_run: Post {post.id} next run is Null. Updating next run")
            await update_next_run(post)
            return False
        elif post.next_run < current_time:
            logger.debug(f"check_next_run: Post {post.id} next run is less than current_time.  Posting status")
            return True
        else:
            logger.debug(f"check_next_run: Post {post.id} next run is greater than current_time.  Not posting status")
            return False
    except Exception as e:
        logger.error(f"check_next_run: {e}")

async def update_next_run(post):
    try:
        schedule = croniter.croniter(post.crontab_schedule)
        next_run = schedule.get_next(datetime)
        with get_db() as db:
            db.query(models.Post).filter(models.Post.id == post.id).update({"next_run": next_run})
            db.commit()
            logger.debug(f"update_next_run: Post {post.id} next run updated to {next_run}")
    except Exception as e:
        logger.error(f"update_next_run: {e}")


async def post_status(post):
    try:
        logger.debug(f"post_status: Checking post {post.id} status")
        bot_token = await get_bot_token(post.bot_token_id)
        if post.bot_token_id == None:
            logger.error(f"post_status: Post {post.id} bot_token_id is Null")
            return False
        else:
            if bot_token == None:
                logger.error(f"post_status: Post {post.id} bot_token is Null")
                return False
            else:
                # Check for media_path and upload media if it exists
                if post.media_path != None:
                    logger.debug(f"post_status: Post {post.id} has media_path.  Uploading media")
                    media_id = await upload_media(post)
                    # add media_id to media_ids list
                    if media_id == None:
                        logger.error(f"post_status: Post {post.id} media_id returned Null")
                        media_ids = None
                    else:
                        media_ids = [media_id]
                        logger.debug(f"post_status: Post {post.id} media_ids: {media_ids}")
                else:
                    media_ids = None
                    logger.debug(f"post_status: Post {post.id} has no media_path.  Not uploading media")
                # Post status
                headers = {
                "Authorization": f"Bearer {bot_token}",
                }
                # Conver payload to json
                data = json.dumps({
                    "status": post.content,
                    "sensitive": post.sensitive,
                    "spoiler_text": post.spoiler_text,
                    "visibility": post.visibility,
                    "media_ids": media_ids
                })
                logger.debug(f"post_status: Post {post.id} data: {data}")
                if quiet_mode() == True:
                    logger.warning(f"post_status: Quiet mode is enabled.  Status {post.id} not posted")
                    # Update post_log table with post_id and last_posted
                    await update_post_log(post)
                    return True
                else:
                    async with aiohttp.ClientSession() as session:
                        async with session.post(f"{settings.mastodon_base_url}/api/v1/statuses", headers=headers, data=data) as response:
                            if response.status == 200:
                                # Update post_log table with post_id and last_posted
                                await update_next_run(post)
                                await update_post_log(post)
                                logger.info(f"post_status: Status {post.id} posted successfully at {datetime.now()}")
                                logger.debug(f"post_status: Status {post.id} response: {await response.json()}")
                                return True
                            else:
                                await update_next_run(post)
                                logger.error(f"post_status: Status {post.id} not posted.  Response status: {response.status}")
                                logger.debug(f"post_status: Status {post.id} response: {await response.json()}")
                                return False
    except Exception as e:
        logger.error(f"post_status: {e}")

async def update_post_log(post):
    try:
        last_posted=datetime.now()
        logger.debug(f"update_post_log: Updating post_log table with post {post.id} and last_posted {last_posted}")
        with get_db() as db:
            # add post to post_log table
            db_post_log = models.PostLog(
                post_id=post.id,
                last_posted=last_posted
            )
            db.add(db_post_log)
            db.commit()
        return True            
    except Exception as e:
        logger.error(f"update_post: {e}")

async def get_bot_token(bot_token_id):
    try:
        with get_db() as db:
            bot_token = db.query(models.BotToken).filter(models.BotToken.id == bot_token_id).first()
            return bot_token.token
    except Exception as e:
        logger.error(f"get_bot_token: {e}")

# Use AIOHTTP to upload media and return media_id, include error handling and logging
# POST /api/v2/media HTTP/1.1
# https://docs.joinmastodon.org/methods/media/
async def upload_media(post):
    try:
        logger.debug(f"upload_media: Uploading media for post {post.id} media_path {post.media_path}")
        # with the media_path open check file has has a mime type and upload media
        with open(post.media_path, "rb") as media:
            media_mime_type = magic.from_buffer(media.read(1024), mime=True)
            logger.debug(f"upload_media: Post {post.id} media_mime_type {media_mime_type}")
            # reset file pointer to start of file
            media.seek(0)
            # get bot_token from post.bot_token_id
            bot_token = await get_bot_token(post.bot_token_id)
            # upload media
            headers = {
                "Authorization" : f"Bearer {bot_token}"
            }
            data = {
                "file": media
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{settings.mastodon_base_url}/api/v2/media", headers=headers, data=data) as response:
                    if response.status == 200 or response.status == 202:
                        # logger debug response
                        logger.debug(f"upload_media: Response for post {post.id} media_path {post.media_path} media_mime_type {media_mime_type} {await response.text()}")
                        # extract id from json response
                        media_id = (await response.json())['id']
                        logger.debug(f"upload_media: Media uploaded successfully for post {post.id} media_id {media_id}")
                        return media_id
                    elif response.status == 422:
                        logger.error(f"upload_media: Error uploading media for post {post.id} media_path {post.media_path} media_mime_type {media_mime_type}")
                        return None
                    else:
                        logger.error(f"upload_media: Error uploading media for post {post.id}")
                        return None
    except Exception as e:
        logger.error(f"upload_media: {e}")


async def clear_next_run():
    try:
        with get_db() as db:
            logger.debug("clear_next_run: Clearing next_run values")
            # get all posts
            posts = db.query(models.Post).all()
            for post in posts:
                # update next_run to Null
                db.query(models.Post).filter(models.Post.id == post.id).update({"next_run": None})
                db.commit()
        return True
    except Exception as e:
        logger.error(f"clear_next_run: {e}")

async def clock_bot_main():
    while True:
        await check_scheduled_posts()
        await asyncio.sleep(10)
       