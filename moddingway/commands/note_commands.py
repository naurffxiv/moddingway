import discord
from discord.ext.commands import Bot
from moddingway.util import is_user_moderator
from .helper import create_logging_embed, create_response_context
from moddingway.services import note_service
from moddingway.database import notes_database
import logging

logger = logging.getLogger(__name__)


class NoteDeleteView(discord.ui.View):
    def __init__(self, note_id: int, interaction: discord.Interaction, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.note_id = note_id
        self.original_interaction = interaction

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.success)
    async def confirm_button_callback(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.clear_items()
        await self.original_interaction.edit_original_response(view=self)
        async with create_response_context(interaction) as response_message:
            async with create_logging_embed(
                self.original_interaction, note_id=self.note_id
            ) as logging_embed:
                msg = await note_service.delete_user_note(logging_embed, self.note_id)

                response_message.set_string(msg)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def cancel_button_callback(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.clear_items()
        await self.original_interaction.edit_original_response(view=self)
        async with create_response_context(interaction) as response_message:
            response_message.set_string("Note deletion cancelled")


def create_note_commands(bot: Bot) -> None:
    @bot.tree.command()
    @discord.app_commands.check(is_user_moderator)
    @discord.app_commands.describe(user="User to add note to")
    async def add_note(
        interaction: discord.Interaction,
        user: discord.User,
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
    async def view_notes(interaction: discord.Interaction, user: discord.User):
        """View the notes of the user"""
        async with create_response_context(interaction) as response_message:
            note_details = await note_service.get_user_notes(user)
            response_message.set_string(note_details)

    @bot.tree.command()
    @discord.app_commands.check(is_user_moderator)
    @discord.app_commands.describe(note_id="Note id to delete")
    async def delete_note(
        interaction: discord.Interaction,
        note_id: int,
    ):
        note_row = await note_service.get_note_by_id(note_id)
        if note_row:
            await interaction.response.send_message(
                f"Are you sure you want to delete this note? \n{note_row}",
                view=NoteDeleteView(
                    note_id=note_id, interaction=interaction, timeout=30
                ),
                ephemeral=True,
            )

        else:
            await interaction.response.send_message("Note not found", ephemeral=True)

    @bot.tree.command()
    @discord.app_commands.check(is_user_moderator)
    @discord.app_commands.describe(note_id="Note id to update")
    async def edit_note(
        interaction: discord.Interaction,
        new_note: str,
        note_id: int,
    ):
        async with create_response_context(interaction) as response_message:
            async with create_logging_embed(
                interaction, new_note=new_note
            ) as logging_embed:
                msg = await note_service.update_user_note(
                    logging_embed, interaction.user, new_note, note_id
                )

                response_message.set_string(msg)
