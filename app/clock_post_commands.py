from .config import settings
from .database import get_db
from . import models, schemas

import re
import random
from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException, status, Response, File, UploadFile
import asyncio
import aiohttp
import json
import croniter
import magic

import logging

logger = logging.getLogger(__name__)

''' CHECK COMMANDS
*********************************************************************************************************************
'''

# Handler to check post.content for commands inside of e.g. {{posts_random: 1}} or {{posts_static: 1}} with variable and call that function from clock_post_commands.py
# Return the result of that function and replace the command with the result
async def check_post_commands(post):
    try:
        logger.debug(f"check_post_commands: Checking post {post.id} for commands")
        # Use regular expression to search for commands in post.content
        commands = re.findall(r'{{\s*(.*?)\s*}}', post.content)
        for command in commands:
            # Split command into function and variable
            function, variable = command.split(":", 1) # split only the first ":" in the string the rest will be in variable
            function = function.strip()
            variable = variable.strip()
            # Call function from clock_post_commands.py
            logger.debug(f"check_post_commands: Post {post.id} function: {function} variable(s): {variable}")
            # Split variable into multiple variables
            variables = variable.split(",")
            # put variables into a list
            variables_list = []
            for variable in variables:
                variables_list.append(variable.strip())
            # Call function from clock_post_commands.py
            result = await globals()[function](*variables_list)
            # Check if result is False and replace with empty string
            if not result:
                result = ""
            # Replace command with result
            post.content = post.content.replace(f"{{{{{command}}}}}", result, 1) # replace the first command that matches

        logger.debug(f"check_post_commands: Post {post.id} content: {post.content}")
        return post
    except Exception as e:
        logger.error(f"check_post_commands: {e}")
        return post

''' COMMANDS
*********************************************************************************************************************
'''

# Function to randomly select a item from a list
async def list_random(list_id: int):
    try:
        with get_db() as db:
            logger.debug(f'Getting random list content from database for list ID {str(list_id)}')
            db_list = db.query(models.List).filter(models.List.id == list_id).first()
            if not db_list:
                logger.error(f'List with ID {str(list_id)} was not found.')
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"List with ID {str(list_id)} was not found.")
            else:
                db_list_content = db.query(models.ListContent).filter(models.ListContent.list_id == list_id).all()
                if not db_list_content:
                    logger.error(f'List with ID {str(list_id)} has no content.')
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                        detail=f"List with ID {str(list_id)} has no content.")
                else:
                    random_item = random.choice(db_list_content)
                    logger.debug(f'Random item from list ID {str(list_id)} is {random_item.content}')
                    return str(random_item.content)
    except Exception as e:
        logger.error(f"random_list: {e}")
        return False

# Function to select a static item from a list
async def list_static(list_id: int, item_id: int):
    try:
        with get_db() as db:
            # Get list from database with list_id
            logger.debug(f'Getting static list content from database for list ID {str(list_id)}')
            db_list = db.query(models.List).filter(models.List.id == list_id).first()
            if not db_list:
                logger.error(f'List with ID {str(list_id)} was not found.')
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"List with ID {str(list_id)} was not found.")
            else:
                # Get list content from database with list_id and item_id
                db_list_content = db.query(models.ListContent).filter(models.ListContent.list_id == list_id, models.ListContent.item_id == item_id).first()
                if not db_list_content:
                    logger.error(f'Item with ID {str(item_id)} was not found in list with ID {str(list_id)}.')
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                        detail=f"Item with ID {str(item_id)} was not found in list with ID {str(list_id)}.")
                else:
                    logger.debug(f'Static item from list ID {str(list_id)} is {db_list_content.content}')
                    return str(db_list_content.content)
    except Exception as e:
        logger.error(f"static_list: {e}")
        return False
        
# Function to get dynamic text from a API endpoint
# Enpoint must return a JSON object vlaue
# Variables passed to fucntion are:
# 1. API endpoint
# 2. JSON object key
# Example: https://stranger.social/api/v1/instance {{dynamic:https://stranger.social/api/v1/instance,key}}
# key will be sent as eg. "stats.user_count"
async def dynamic(endpoint: str, key: str):
    try:
        logger.debug(f"dynamic: Getting dynamic text from API endpoint {endpoint}")
        async with aiohttp.ClientSession() as session:
            async with session.get(endpoint) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.debug(f"dynamic: API endpoint {endpoint} returned {data}")
                    # Get value from JSON object
                    value = data
                    for key in key.split("."):
                        value = value.get(key)
                    if not value:
                        logger.error(f"dynamic: Key {key} does not exist in JSON object")
                        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                            detail=f"Key {key} does not exist in JSON object")
                    else:
                        logger.debug(f"dynamic: Value {value} from key {key} in JSON object")
                        return str(value)
                else:
                    logger.error(f"dynamic: API endpoint {endpoint} returned {response.status}")
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                        detail=f"API endpoint {endpoint} returned {response.status}")
    except Exception as e:
        logger.error(f"dynamic: {e}")
        return False

# Function to get randmon media from a list
# Variables passed to fucntion are:
# 1. list_id of media list
async def media_random(list_id: int):
    try:
        with get_db() as db:
            logger.debug(f'media_random: Getting random media from database for list ID {str(list_id)}')
            db_list = db.query(models.List).filter(models.List.id == list_id).first()
            if not db_list:
                logger.error(f'media_random: List with ID {str(list_id)} was not found.')
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"List with ID {str(list_id)} was not found.")
            else:
                db_list_content = db.query(models.ListContent).filter(models.ListContent.list_id == list_id).all()
                if not db_list_content:
                    logger.error(f'media_random: List with ID {str(list_id)} has no content.')
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                        detail=f"List with ID {str(list_id)} has no content.")
                else:
                    random_item = random.choice(db_list_content)
                    logger.debug(f'media_random: Random item from list ID {str(list_id)} is {random_item.content}')
                    return str(random_item.content)
    except Exception as e:
        logger.error(f"media_random: {e}")
        return False