import discord
from services.exile_service import exile_user
from util import calculate_time_delta
from typing import Optional
from .helper import create_modal_embed


class ExileModal(discord.ui.Modal):
    def __init__(self, user: discord.Member) -> None:
        super().__init__(title=f"Exile User {user.display_name}")
        self.user = user

    duration = discord.ui.TextInput(label="Exile Duration")

    reason = discord.ui.TextInput(
        label="Exile Reason",
        style=discord.TextStyle.long,
        placeholder="Why is the user exiled",
        max_length=300,
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):

        async with create_modal_embed(
            interaction,
            "Exile User",
            user=self.user,
            duration=self.duration.value,
            reason=self.reason.value,
        ) as logging_embed:
            exile_duration = calculate_time_delta(self.duration.value)
            error_message = await exile_user(
                logging_embed, self.user, exile_duration, self.reason.value
            )

            await interaction.response.send_message(
                error_message or f"Successfully exiled {self.user.mention}",
                ephemeral=True,
            )


class ExileModalOneDay(ExileModal):
    duration = discord.ui.TextInput(label="Exile Duration", default="1d")


class ExileModalOneHour(ExileModal):
    duration = discord.ui.TextInput(label="Exile Duration", default="1h")
