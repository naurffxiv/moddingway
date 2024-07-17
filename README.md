# Moddingway

Discord moderation bot for NAUR.

## How To Run
Run `docker compose up --build` after providing the appropriate environment variables listed below in the `.env` file.

### Release
#### Environment variables:
- DISCORD_TOKEN
- POSTGRES_USER
- POSTGRES_PASSWORD

### Testing
#### Environment variables:
- DISCORD_TOKEN
- POSTGRES_USER
- POSTGRES_PASSWORD
- DEBUG
- GUILD_ID
- MOD_LOGGING_CHANNEL_ID

`DEBUG` must be set to true

