import discord
from services.exile_service import exile_user
from util import calculate_time_delta


class ExileModal(discord.ui.Modal):

    def __init__(self, user: discord.Member) -> None:
        self.user = user
        super().__init__(title=f"Exile User {user.display_name}")

    duration = discord.ui.TextInput(label="Exile Duration", default="1d")

    reason = discord.ui.TextInput(
        label="Exile Reason",
        style=discord.TextStyle.long,
        placeholder="Why is the user exiled",
        max_length=300,
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        # TODO set up corrext context management here
        embed = discord.Embed()

        exile_duration = calculate_time_delta(self.duration.value)
        error_message = await exile_user(
            embed, self.user, exile_duration, self.reason.value
        )

        await interaction.response.send_message(
            error_message or f"Successfully exiled {self.user.mention}", ephemeral=True
        )
