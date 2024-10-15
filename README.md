# Moddingway

Discord moderation bot for NAUR.

## How To Run
Run `make start` after providing the appropriate environment variables listed below in the `.env` file.

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
- DISCORD_TOKEN
- POSTGRES_HOST
- POSTGRES_PORT
- POSTGRES_DB
- POSTGRES_USER
- POSTGRES_PASSWORD
- DEBUG
- GUILD_ID
- MOD_LOGGING_CHANNEL_ID

`DEBUG` must be set to `true` for testing.  
Defaults are also set for `POSTGRES_PORT` (5432) and `POSTGRES_DB` (moddingway) if those two are not set.

This is a test
