import discord
from services.ban_service import ban_user


class BanModal(discord.ui.Modal):

    def __init__(self, user: discord.Member) -> None:
        self.user = user
        super().__init__(title=f"Ban User {user.display_name}")

    reason = discord.ui.TextInput(
        label="Ban Reason",
        style=discord.TextStyle.long,
        placeholder="Why is the user banned",
        max_length=300,
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        # TODO set up corrext context management here
        embed = discord.Embed()
        await ban_user(embed, self.user, self.reason.value)

        await interaction.response.send_message(
            f"Successfully banned {self.user.mention}", ephemeral=True
        )
