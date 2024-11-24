import discord
from discord.ext.commands import Bot
from util import is_user_moderator
from enums import StrikeSeverity
from .helper import create_logging_embed, create_response_context
from services import strike_service


def create_strikes_commands(bot: Bot) -> None:
    @bot.tree.command()
    @discord.app_commands.check(is_user_moderator)
    @discord.app_commands.describe(user="User being striked")
    async def add_strike(
        interaction: discord.Interaction,
        user: discord.Member,
        severity: StrikeSeverity,
        reason: str,
    ):
        """Add a strike to the user"""
        async with create_response_context(interaction) as response_message:
            async with create_logging_embed(
                interaction, user=user, reason=reason, severity=severity.name
            ) as logging_embed:

                await strike_service.add_strike(
                    logging_embed, user, severity, reason, interaction.user
                )

                response_message.set_string(
                    f"Successfully added strike to  {user.mention}"
                )
