import discord
import logging
from typing import Optional, Tuple
from moddingway.util import send_dm
from moddingway.settings import get_settings
from datetime import datetime, timedelta, timezone

settings = get_settings()
logger = logging.getLogger(__name__)


async def ban_user(
    user: discord.Member, reason: str, delete_messages: bool
) -> Optional[Tuple[bool, str]]:
    """Executes ban of user.

     Args:
         user (discord.Member): The user being banned.
         reason (str): Reason for the ban.
         delete_messages_flag (bool): Whether to delete the user's messages.

    Returns:
         bool: status of the ban
         str: any errors that occurred
    """
    if len(reason) >= 512:
        return (
            False,
            f"Unable to ban {user.mention}: reason is too long (above 512 characters). Please shorten the ban reason.",
        )

    # Calculate the timestamp for 30 days from now
    appeal_deadline = int((datetime.now(timezone.utc) + timedelta(days=30)).timestamp())

    dm_failed_message = None
    try:
        await send_dm(
            user,
            f"Hello {user.display_name},\n\n"
            "You are being informed that you have been **banned** from **NA Ultimate Raiding - FFXIV**.\n\n"
            "**Reason for the ban:**\n"
            f"> {reason}\n\n"
            f"If you believe this ban was issued in error you can reach out to the Moderation Team. Otherwise, you may appeal this ban starting on <t:{appeal_deadline}:F>.\n\n"
            "Please note that any further attempts to rejoin the server will be met with a permanent ban.\n\n",
        )
    except Exception as e:
        err = f"Failed to send DM to {user.mention}: {e}"
        logger.error(err)
        dm_failed_message = err

    try:
        # 604800 seconds is the maximum value for delete_message_seconds, and is equivalent to 7 days.
        delete_seconds = 604800 if delete_messages else 0
        await user.ban(reason=reason, delete_message_seconds=delete_seconds)
        logger.info(f"Successfully banned {user.mention}")

        return True, dm_failed_message
    except Exception as e:
        logger.error(f"Failed to ban {user.mention}: {e}")
        return (
            False,
            f"Failed to ban {user.mention}. Please try again or use Discord's built-in tools.",
        )
