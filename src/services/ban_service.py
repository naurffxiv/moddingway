import discord
import logging
from util import log_info_and_embed, send_dm

logger = logging.getLogger(__name__)


async def ban_user(logging_embed: discord.Embed, user: discord.Member, reason: str):
    log_info_and_embed(logging_embed, logger, f"going to ban {user.mention}")

    log_info_and_embed(logging_embed, logger, f"because {reason}")

    #TO DO: When the appeal process is implemented, add a link to the appeal process in the message.
    await send_dm(
        user,
        f"You are being banned from NA Ultimate Raiding - FF XIV for the following reason: \n> {reason} \
        \nYou may appeal this ban by contacting the moderators of the server in 30 days.",
    )

    await user.ban(reason=reason)
