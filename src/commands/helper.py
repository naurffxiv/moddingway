from contextlib import asynccontextmanager
import discord
from discord.ext.commands import Bot
from settings import get_settings
from util import EmbedField, create_interaction_embed_context
import logging
import time

settings = get_settings()
logger = logging.getLogger(__name__)


def create_logging_embed(interaction: discord.Interaction, **kwargs):
    fields = [EmbedField("Action", f"/{interaction.command.name}")]
    # Dynamically add kwargs to fields
    if kwargs is not None:
        for key, value in kwargs.items():
            key = key.replace("_", " ")
            match (type(value)):
                case discord.Member:
                    fields.append(EmbedField(key.title(), f"<@{value.id}>"))
                case discord.ChannelType:
                    fields.append(EmbedField(key.title(), f"<#{value}>"))
                case _:
                    fields.append(EmbedField(key.title(), value))

    return create_interaction_embed_context(
        interaction.guild.get_channel(settings.logging_channel_id),
        user=interaction.user,
        timestamp=interaction.created_at,
        description=f"Used `{interaction.command.name}` command in {interaction.channel.mention}",
        fields=fields,
    )


def create_bot_errors(bot: Bot) -> None:
    @bot.tree.error
    async def on_app_command_error(interaction: discord.Interaction, error):
        # Handle CommandOnCooldown error
        if isinstance(error, discord.app_commands.CommandOnCooldown):
            remaining_time = int(error.retry_after) + int(time.time())
            await interaction.response.send_message(
                f"This command is on cooldown. Try again <t:{remaining_time}:R>.",
                ephemeral=True,
            )

        # Handle CheckFailure error
        elif isinstance(error, discord.app_commands.CheckFailure):
            await interaction.response.send_message(
                "You do not have the 'Mod' role to use this command.",
                ephemeral=True,
            )

        # Handle other errors (default fallback)
        else:
            logger.error(f"An unexpected error has occurred: {error}")
            try:
                await interaction.response.send_message(
                    "An unexpected error occurred. Please contact an admin.",
                    ephemeral=True,
                )
            except discord.InteractionResponded:
                # If interaction response has already been sent
                logger.warning("Interaction already responded to.")


@asynccontextmanager
async def create_response_context(interaction: discord.Interaction, sendEphemeral=True):
    # Can't yield a string since it's immutable, so create a helper class
    class ResponseHelper:
        def __init__(self):
            self.message = ""

        def set_string(self, message):
            self.message = message

        def append_string(self, message):
            self.message = f"{self.message}\n{message}"

    await interaction.response.send_message("Processing...", ephemeral=sendEphemeral)
    helper = ResponseHelper()
    try:
        yield helper
    except Exception as e:
        helper.append_string(e)
    finally:
        try:
            msg = await interaction.original_response()
            if len(helper.message) == 0:
                helper.set_string("Command finished without a response.")
            await msg.edit(content=helper.message)
        except Exception as e:
            logger.error("Updating placeholder message failed")
