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


Defaults are also set for `POSTGRES_PORT` (5432) and `POSTGRES_DB` (moddingway) if those two are not set.

To run a dockerized version of our postgres database locally, run `docker compose -f postgres.yml up postgres_local`. To run this, you will need to install and run [docker desktop](https://www.docker.com/products/docker-desktop/) on your local machine. The python bot will create the tables it needs when you first run it

## Development recommendations

#### Black Formatter
Files in this repo will be run through the [Black Formatter](https://black.readthedocs.io/en/stable/). To minimize merge conflicts, it is recommended to run this formatter on your code before submitting. Most IDEs will have an extension for black, and it is recommended to use those