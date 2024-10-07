import discord
from discord.ext.commands import Bot
from settings import get_settings
from services.exile_service import exile_user, unexile_user
from util import is_user_moderator
from .helper import create_logging_embed

settings = get_settings()


def create_exile_commands(bot: Bot) -> None:
    @bot.tree.command()
    @discord.app_commands.check(is_user_moderator)
    @discord.app_commands.describe(user="User being exiled")
    async def unexile(interaction: discord.Interaction, user: discord.Member):
        """Unexile the specified user."""

        async with create_logging_embed(interaction) as logging_embed:
            await unexile_user(logging_embed, user)

            await interaction.response.send_message(
                f"Successfully unexiled {user.mention}", ephemeral=True
            )

    @bot.tree.command()
    @discord.app_commands.check(is_user_moderator)
    @discord.app_commands.describe(
        user="User being exiled",
        duration="The duration of the exile. TBA format",
        reason="Reason for exile",
    )
    async def exile(
        interaction: discord.Interaction,
        user: discord.Member,
        duration: str,
        reason: str,
    ):
        """Exile the specified user."""

        async with create_logging_embed(interaction) as logging_embed:
            await exile_user(logging_embed, user, duration, reason)

            await interaction.response.send_message(
                f"Successfully exiled {user.mention}", ephemeral=True
            )
