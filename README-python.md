# Moddingway

Discord moderation bot for NAUR.

### Environment variables
Postgres-related information is configured in the environment variables instead of a pre-created user/password.
#### Release
- DISCORD_TOKEN
- POSTGRES_HOST
- POSTGRES_PORT
- POSTGRES_DB
- POSTGRES_USER
- POSTGRES_PASSWORD

#### Testing
- GUILD_ID
- DISCORD_TOKEN
- MOD_LOGGING_CHANNEL_ID
- POSTGRES_PASSWORD

`DEBUG` must be set to `true` for testing.  
Defaults are also set for `POSTGRES_PORT` (5432) and `POSTGRES_DB` (moddingway) if those two are not set.

## Development recommendations

#### Black Formatter
Files in this repo will be run through the [Black Formatter](https://black.readthedocs.io/en/stable/). To minimize merge conflicts, it is recommended to run this formatter on your code before submitting. Most IDEs will have an extension for black, and it is recommended to use those