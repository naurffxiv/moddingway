# TODO: [MOD-92] Decomm Modals
import discord
from services.exile_service import exile_user
from util import calculate_time_delta
from .helper import create_modal_embed
from commands.helper import create_response_context


class ExileModal(discord.ui.Modal):
    def __init__(
        self, user: discord.Member, duration: str, duration_title: str
    ) -> None:
        super().__init__(title=f"Exile User {user.display_name} for {duration_title}")
        self.duration_string = duration
        self.exile_duration = calculate_time_delta(duration)

        if self.exile_duration is None:
            raise Exception("Bad exile duration in code")

        self.user = user

    reason = discord.ui.TextInput(
        label="Exile Reason",
        style=discord.TextStyle.long,
        placeholder="Reason for exiling user",
        max_length=512,
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        async with create_response_context(interaction) as response_message:
            async with create_modal_embed(
                interaction,
                "Exile User",
                user=self.user,
                duration=self.duration_string,
                reason=self.reason.value,
            ) as logging_embed:
                error_message = await exile_user(
                    logging_embed, self.user, self.exile_duration, self.reason.value
                )

                response_message.set_string(
                    error_message or f"Successfully exiled {self.user.mention}"
                )
