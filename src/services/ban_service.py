import discord
import logging
from typing import Optional, Tuple
from util import log_info_and_embed, send_dm
from settings import get_settings
from datetime import datetime, timedelta, timezone

settings = get_settings()
logger = logging.getLogger(__name__)


async def ban_user(
    invoking_member: discord.Member,
    user: discord.Member,
    reason: str,
    delete_messages_flag: bool,
) -> Optional[Tuple[bool, str]]:
    """Executes ban of user.

    Args:
        invoking_member (discord.Member): The moderator initiating the ban.
        user (discord.Member): The user being banned.
        reason (str): Reason for the ban.
        delete_messages_flag (bool): Whether to delete the user's messages.

    Returns:
        Optional[Tuple[bool, bool, str]]: Result of the ban operation. Tuple contains:
            - bool: True if ban was successful, False otherwise.
            - str: Description of the result of the ban operation
    """
    if len(reason) >= 512:
        return (
            False,
            f"Unable to ban {user.mention}: reason is too long (above 512 characters). Please shorten the ban reason.",
        )

    # Ensure invoking_member has a higher role position than the target user.
    if user.top_role >= invoking_member.top_role:
        return (
            False,
            f"Unable to ban {user.mention}: You cannot ban a user with an equal or higher role than yourself.",
        )

    # Calculate the timestamp for 30 days from now
    appeal_deadline = int((datetime.now(timezone.utc) + timedelta(days=30)).timestamp())

    dm_state = False
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
        logger.error(f"Failed to send DM to {user.mention}: {e}")

    try:
        # We typically do NOT want to delete messages, as we want to preserve evidence.
        # However, we may want to delete messages in cases where the user has posted inappropriate content or spam.
        # Delete messages only if delete_messages is True
        # 604800 seconds is the maximum value for delete_message_seconds, and is equivalent to 7 days.
        delete_seconds = 604800 if delete_messages_flag else 0
        await user.ban(reason=reason, delete_message_seconds=delete_seconds)
        logger.info(f"Successfully banned {user.mention}")
        return (True, f"Successfully banned {user.mention}.")
    except Exception as e:
        logger.error(f"Failed to ban {user.mention}: {e}")
        return (
            False,
            f"Failed to ban {user.mention}. Please try again or use Discord's built-in tools.",
        )
