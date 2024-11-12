# Moddingway

Discord moderation bot for NAUR.

### Environment variables
Postgres-related information is configured in the environment variables instead of a pre-created user/password. For local development, you can create a `.env` file to populate the following environment variables

#### Testing
- GUILD_ID
- DISCORD_TOKEN
- MOD_LOGGING_CHANNEL_ID
- POSTGRES_USER
- POSTGRES_PASSWORD
- POSTGRES_DB

#### Release
- DISCORD_TOKEN
- POSTGRES_HOST
- POSTGRES_PORT
- POSTGRES_DB
- POSTGRES_USER
- POSTGRES_PASSWORD
- DEBUG
- GUILD_ID
- MOD_LOGGING_CHANNEL_ID
- INACTIVE_FORUM_CHANNEL_ID
- INACTIVE_FORUM_DURATION
- NOTIFY_CHANNEL_ID


Defaults are also set for `POSTGRES_PORT` (5432) and `POSTGRES_DB` (moddingway) if those two are not set.
`INACTIVE_FORUM_CHANNEL_ID` and `INACTIVE_FORUM_DURATION` are optional. The relevant task will not run if those environment variables are not defined.

To run a dockerized version of our postgres database locally, run `make database-run`. To run this, you will need to install and run [docker desktop](https://www.docker.com/products/docker-desktop/) on your local machine. The python bot will create the tables it needs when you first run it

## Development recommendations

### First time setup
When you first are setting up the application, copy the file titled `.env_example` to be `.env`, and configure the missing enviornment variables. To add the bot account to your server, you can follow the [discord.py instructions](https://discordpy.readthedocs.io/en/stable/discord.html). The server that you use for development also will need to have a channel where the bot will output logging messages, and will need to have the following roles set up
* Exiled
* Verified
* Administration
* Management

In addition, you will need to give yourself either the `Admin` or `Mod` role in order to properly run all commands.

### Black Formatter
Files in this repo will be run through the [Black Formatter](https://black.readthedocs.io/en/stable/). To minimize merge conflicts, it is recommended to run this formatter on your code before submitting. Most IDEs will have an extension for black, and it is recommended to use those

### Running in Docker
If you want to run the app in a container, you run the application via `make python-run`. This command will also create a container for the postgres database, and will override the postgres host environment variable to correctly allow the two containers to interact with each other
