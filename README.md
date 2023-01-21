# clock-bot

A Python FastAPI bot that can be used send post to a Matodon Instance on a schedule.

## Get API Key

To use this bot, you will need to create a bot account on your Mastodon instance. You can do this by going to your instance's settings page under Development, and creating a new application. The bot requires  `write:media` and `write:statuses` permissions. Copy the access token for the bot account, and paste it into the .env file.

The bot requires no special permissions.  Do not give the bot admin permissions.

## Installation

1. Clone this repository
2. Create .env file from the .env.example file
3. Fill in the .env file with your Mastodon instance's information
4. Run `docker-compose up --build -d` to start the bot.
5. Run `docker ps -a` to see the container ID of the bot.
6. Run `docker exec -ti [container_id] /bin/bash` to enter the container.
7. Run Alembic migrations by running `alembic upgrade head` in the container.
8. Run `docker-compose restart` to restart the bot.
9. Initiate admin user by visiting http://localhost:8088/docs#/Admin/init_admin_admin_init_post. 


## Environment Variables

The following environment variables are required to run the bot, and should be set in the .env file.

```
API_PORT=8089
QUIET=True/False
LOGGING_LEVEL=INFO
MASTODON_ACCESS_TOKEN=The access token for your bot account on your Mastodon instance (e.g. stranger.social)
MASTODON_BASE_URL=The base URL for your Mastodon instance (e.g. https://stranger.social)
DATABASE_HOSTNAME=postgres
DATABASE_PORT=5432
DATABASE_PASSWORD=password
DATABASE_NAME=clockbot
DATABASE_USERNAME=postgres
SECRET_KEY=Use genkey.py to generate a secret key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=2
TZ=UTC # Do not change this
```

## Usage

### Controls

The bot can be controlled by visiting http://localhost:8088/docs.  It is designed to be operated from an external application, such as a mobile app.  The docs allow you full access to all the features of the bot. Including admin functions and user control. Refer to the docs for more information.

## TODO

- [X] Add support for multiple bots
- [X] Include media in posts
- [ ] Add descriptions and focus to media files
- [ ] Randmoize posts from list
- [ ] Randomize posts from list with media
- [ ] Add keywords to posts to be used in randomization
- [ ] Add keywords to posts get data from external sources (e.g. API calls)
- [ ] Add ability to send messages to bot users for error reporting
- [ ] Include media in posts
- [ ] Randmoize posts from list
- [ ] Randomize posts from list with media
- [ ] Send manual posts
- [ ] Silence individual bots accounts for a period of time
- [ ] Silence individual bots accounts permanently
- [ ] Adjust timezones for individual bots
- [ ] Schedule posts for individual bots without using cron
- [ ] Add ability to offset posts by a random amount of time (e.g. 1-5 minutes)
- [ ] Add ability to send messages to groups of bots
- [ ] Add ability to trigger bot based on events (e.g. new follower, new toot, trending hashtag, etc.)
- [ ] More error handling!!!


## Revisions

### 0.1.0

- Initial release

### 0.2.1

- Add media to post
