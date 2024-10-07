import discord
from settings import get_settings
import enums
from enums import Role

settings = get_settings()


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
    member: discord.Member, role_to_add: enums.Role, role_to_remove: enums.Role
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


def user_has_role(user: discord.Member, role: enums.Role) -> bool:
    return any(
        discord_role
        for discord_role in user.guild.roles
        if discord_role.name == role.value
    )


async def is_user_moderator(interaction: discord.Interaction):
    return user_has_role(interaction.user, Role.ADMINISTRATION) or user_has_role(
        interaction.user, Role.MANAGEMENT
    )
