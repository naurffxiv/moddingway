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
We recommend getting a [virtual environment](https://docs.python.org/3/library/venv.html) set up for python before you start development. All required packages to run the application are defined in `requirements.txt`

When you first are setting up the application, copy the file titled `.env_example` to be `.env`, and configure the missing enviornment variables. To add the bot account to your server, you can follow the [discord.py instructions](https://discordpy.readthedocs.io/en/stable/discord.html). The server that you use for development also will need to have a channel where the bot will output logging messages, and will need to have the following roles set up, in this priority order
* Mod
* Verified
* Exiled

In addition, you will need to give yourself the `Mod` role in order to properly run all moderation commands.


## Testing
This application uses pytest to run automated unit tests. To install pytest, run `pip install pytest`. To confirm that pytest installed properly, run the command `pytest --version` and you should get an output like `pytest 8.3.4`. If you get an error related to the command being missing, you must either add the pytest install to your path, or you can replace all instances of `pytest` in suggested commands with `python -m pytest`. Alternatively, most IDEs support running tests directly in the IDE with pytest.


### Black Formatter
Files in this repo will be run through the [Black Formatter](https://black.readthedocs.io/en/stable/). To minimize merge conflicts, it is recommended to run this formatter on your code before submitting. Most IDEs will have an extension for black, and it is recommended to use those

### Running in Docker
If you want to run the app in a container, you run the application via `make python-run`. This command will also create a container for the postgres database, and will override the postgres host environment variable to correctly allow the two containers to interact with each other

### Reseeding the Database
By default, when you run the application either via python or docker, records in the database will persist. If you want to reset the database, you can do so by running `make database-clean` while the postgres container is running on your machine. If the database container is not found by the command, you can first start it by running `make database-run`

# API

To get started with moddingway API development, install the necessary packages using `pip install -r requirements-api.txt`. From there, you can start the server by running `make api`. You can then view the swaggerdocs page hosted on `localhost:8000/docs` to view all current endpoints.

Alternatively, if you want to have local changes reflected in realtime with your development API, you can run `make api-reload`