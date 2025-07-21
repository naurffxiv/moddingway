import discord
from discord.ext.commands import Bot
from moddingway.util import is_user_moderator
from .helper import create_logging_embed, create_response_context
from moddingway.services import note_service


def create_warning_commands(bot: Bot) -> None:
    @bot.tree.command()
    @discord.app_commands.check(is_user_moderator)
    @discord.app_commands.describe(user="User to give warning to")
    async def warn(
        interaction: discord.Interaction,
        user: discord.User,
        warning_note: str,
    ):
        """Warns a user"""
        async with create_response_context(interaction) as response_message:
            async with create_logging_embed(
                interaction, user=user, note=warning_note
            ) as logging_embed:
                await note_service.add_note(
                    logging_embed, user, warning_note, interaction.user, True
                )
                response_message.set_string(
                    f"Successfully added warning to {user.mention}"
                )

    @bot.tree.command()
    @discord.app_commands.check(is_user_moderator)
    @discord.app_commands.describe(user="User whose warnings you are viewing")
    async def view_warnings(interaction: discord.Interaction, user: discord.User):
        """View the notes of the user"""
        async with create_response_context(interaction) as response_message:
            note_details = await note_service.get_user_warnings(user)
            response_message.set_string(note_details)
