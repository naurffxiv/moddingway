import discord
from discord.ext.commands import Bot
from moddingway.util import is_user_moderator
from .helper import create_logging_embed, create_response_context
from moddingway.services import note_service


def create_note_commands(bot: Bot) -> None:
    @bot.tree.command()
    @discord.app_commands.check(is_user_moderator)
    @discord.app_commands.describe(user="User to add note to")
    async def add_note(
        interaction: discord.Interaction,
        user: discord.Member,
        note: str,
    ):
        """Add a note to the user"""
        async with create_response_context(interaction) as response_message:
            async with create_logging_embed(
                interaction, user=user, note=note
            ) as logging_embed:
                await note_service.add_note(logging_embed, user, note, interaction.user)

                response_message.set_string(
                    f"Successfully added note to {user.mention}"
                )

    @bot.tree.command()
    @discord.app_commands.check(is_user_moderator)
    @discord.app_commands.describe(user="User whose notes you are viewing")
    async def view_notes(interaction: discord.Interaction, user: discord.Member):
        """View the notes of the user"""
        async with create_response_context(interaction) as response_message:
            note_details = await note_service.get_user_notes(user)
            response_message.set_string(note_details)
