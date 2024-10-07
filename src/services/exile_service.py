import discord
import logging
from util import log_info_and_embed, add_and_remove_role, send_dm
from enums import Role

logger = logging.getLogger(__name__)


async def exile_user(
    logging_embed: discord.Embed, user: discord.Member, duration: str, reason: str
):
    # TODO implement this functionality
    log_info_and_embed(
        logging_embed, logger, f"going to exile {user.mention} for {duration}"
    )

    # Look up

    log_info_and_embed(logging_embed, logger, f"because {reason}")

    # look up user in DB

    # add exile entry into DB

    # change user role
    await add_and_remove_role(user, role_to_add=Role.EXILED, role_to_remove=Role.VERIFIED)


    # message user
    await send_dm(user, f"You are being exiled from NAUR FFXIV for the following reason: {reason}")


async def unexile_user(logging_embed: discord.Embed, user: discord.User):
    await add_and_remove_role(user, Role.VERIFIED, Role.EXILED)
