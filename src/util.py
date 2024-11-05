from contextlib import asynccontextmanager
import discord
from settings import get_settings
import re
from typing import Optional
from datetime import timedelta
from enums import Role

settings = get_settings()


class EmbedField(object):
    name: str
    value: str

    def __init__(self, name, value):
        self.name = name
        self.value = value


class UnableToDM(RuntimeError):
    pass


@asynccontextmanager
async def create_interaction_embed_context(
    log_channel: discord.abc.GuildChannel, **kwargs
):
    # optional args
    user = kwargs.get("user", None)
    description = kwargs.get("description", None)
    timestamp = kwargs.get("timestamp", None)
    footer = kwargs.get("footer", None)
    fields = kwargs.get("fields", None)

    embed = discord.Embed()
    try:
        if user is not None:
            embed.set_author(
                name=user.display_name,
                icon_url=user.display_avatar.url,
            )
        if description is not None:
            embed.description = description
        if timestamp is not None:
            embed.timestamp = timestamp
        if footer is not None:
            embed.set_footer(text=footer)
        if fields is not None:
            for field in fields:
                embed.add_field(name=field.name, value=field.value, inline=False)

        yield embed
    except Exception as e:
        embed.add_field(name="Error", value=e, inline=False)
        raise e
    finally:
        await log_channel.send(embed=embed)


def log_info_and_embed(embed: discord.Embed, logger, message: str):
    """
    Write a log message to both the default logger and add the string to
    the discord message that will be sent to the logging channel upon command
    finishing
    """
    if embed.description is None:
        embed.description = ""
    embed.description += "\n" + message
    logger.info(message)


async def send_dm(member: discord.Member, messageContent: str):
    channel = await member.create_dm()
    await channel.send(content=messageContent)


async def add_and_remove_role(
    member: discord.Member, role_to_add: Role, role_to_remove: Role
):
    discord_role_to_add = None
    discord_role_to_remove = None

    for role in member.guild.roles:
        if role.name == role_to_add.value:
            discord_role_to_add = role
        if role.name == role_to_remove.value:
            discord_role_to_remove = role

    if discord_role_to_add is None:
        # This role does not exist, likely a misconfiguration of the server
        raise Exception(f"Role {role_to_add.value} not found in server")

    if discord_role_to_remove is None:
        # This role does not exist, likely a misconfiguration of the server
        raise Exception(f"Role {role_to_remove.value} not found in server")

    await member.remove_roles(discord_role_to_remove)
    await member.add_roles(discord_role_to_add)


def user_has_role(user: discord.Member, role: Role) -> bool:
    return any(
        discord_role for discord_role in user.roles if discord_role.name == role.value
    )


def calculate_time_delta(delta_string: Optional[str]) -> Optional[timedelta]:
    if not delta_string:
        return None

    regex = "(\d\d?)([smhd])"  # Matches (digit, digit?)(letter in [s, m, h, d])

    result = re.search(regex, delta_string)

    if result:
        duration = int(result.group(1))
        unit = result.group(2)

        delta = None

        if unit == "s":
            delta = timedelta(seconds=duration)
        elif unit == "m":
            delta = timedelta(minutes=duration)
        elif unit == "h":
            delta = timedelta(hours=duration)
        elif unit == "d":
            delta = timedelta(days=duration)

        return delta

    return None


async def is_user_moderator(interaction: discord.Interaction):
    return (
        user_has_role(interaction.user, Role.ADMINISTRATION)
        or user_has_role(interaction.user, Role.MANAGEMENT)
        or user_has_role(interaction.user, Role.MOD)
    )
