import discord
from contextlib import asynccontextmanager
from discord.ext.commands import Bot
from settings import get_settings

settings = get_settings()


@asynccontextmanager
async def create_autounexile_embed(
    self, user: discord.User, exile_id: str, end_timestamp: str
):
    embed = discord.Embed()
    log_channel = self.get_channel(settings.logging_channel_id)
    try:
        embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
        embed.timestamp = end_timestamp
        embed.description = f"<@{user.id}>'s exile has timed out"
        embed.set_footer(text=f"Exile ID: {exile_id}")

        yield embed
    except Exception as e:
        embed.add_field(name="Error", value=e)
        raise e
    finally:
        await log_channel.send(embed=embed)
