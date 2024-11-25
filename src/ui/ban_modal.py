# TODO: [MOD-92] Decomm Modals
import discord
from services.ban_service import ban_user
from .helper import create_modal_embed
from commands.helper import create_response_context


class BanModal(discord.ui.Modal):

    def __init__(self, user: discord.Member) -> None:
        self.user = user
        super().__init__(title=f"Ban User {user.display_name}")

    reason = discord.ui.TextInput(
        label="Ban Reason",
        style=discord.TextStyle.long,
        placeholder="Reason for banning user",
        max_length=512,
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        async with create_response_context(interaction) as response_message:
            async with create_modal_embed(
                interaction,
                "Ban User",
                user=self.user,
                reason=self.reason.value,
            ) as logging_embed:
                await ban_user(logging_embed, self.user, self.reason.value)

                response_message.set_string(f"Successfully banned {self.user.mention}")
