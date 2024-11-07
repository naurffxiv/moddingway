import discord
from services.exile_service import exile_user
from util import calculate_time_delta
from .helper import create_modal_embed
from commands.helper import create_response_context

class ExileModal(discord.ui.Modal):
    def __init__(self, user: discord.Member) -> None:
        super().__init__(title=f"Exile User {user.display_name}")
        self.user = user

    duration = discord.ui.TextInput(label="Exile Duration", required=True)

    reason = discord.ui.TextInput(
        label="Exile Reason",
        style=discord.TextStyle.long,
        placeholder="Reason for exiling user",
        max_length=512,
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        exile_duration = calculate_time_delta(self.duration.value)

        if self.duration.value and not exile_duration:
            # TODO update this string once exile duration change is merged
            await interaction.response.send_message(
                "Invalid exile duration given, duration should be in the form of [1 or 2 digits][s, d, m, h]. No action will be taken",
                ephemeral=True,
            )
            return

        async with create_response_context(interaction) as response_message:
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

                response_message.set_string(
                    error_message or f"Successfully exiled {self.user.mention}"
                )


class ExileModalOneDay(ExileModal):
    duration = discord.ui.TextInput(label="Exile Duration", required=True, default="1d")


class ExileModalOneHour(ExileModal):
    duration = discord.ui.TextInput(label="Exile Duration", required=True, default="1h")
