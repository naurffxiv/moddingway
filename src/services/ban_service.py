import discord
import logging
from typing import Optional,Tuple
from util import log_info_and_embed, send_dm
from settings import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


async def ban_user(
    user: discord.Member, 
    reason: str
) -> Optional[Tuple[bool, str]]:
    if len(reason) < 512: 
        
        result_description = ""
        dm_state = False
        #attempt to send a DM to the user with the reason for the ban
        try:
            await send_dm(
                user,
                f"You are being banned from NA Ultimate Raiding - FF XIV for the following reason: \n> {reason} "
                "\nYou may appeal this ban by contacting the moderators of the server in 30 days."
            )
            dm_info = f"DM sent to {user.mention} with ban reason."
            logger.info("Successfully sent dm to user")
            dm_state = True
        except discord.Forbidden as e:
            dm_info = f"Could not send DM to {user.mention} (DMs disabled or bot blocked)."
            logger.info(f"DM failed to send due to permission error: {e}")
            dm_state = False
        except discord.HTTPException as e:
            dm_info = f"Failed to send DM to {user.mention} due to an HTTP error: {e}."
            logger.info(f"DM failed to send due to HTTP Error: {e}")
            dm_state = False

        #attempt Ban
        try:
            await user.ban(reason=reason)
            logger.info("Successfully banned")
            ban_info = f"Successfully banned {user.mention}."
            result = True
        except discord.Forbidden as e:
            ban_info = f" Failed to ban {user.mention}; insufficient permissions."
            logger.info(f"Ban failed due to permission error: {e}")
            result = False
        except discord.HTTPException as e:
            ban_info = f" An error occurred while banning {user.mention}: {e}."
            logger.info(f"Ban failed due to HTTP Error: {e}")
            result = False
            
    
        if not result and dm_state: #ban fail dm succeed.
            result_description = ban_info + "\n" + dm_info + "\n" + "Ban failed but DM sent, please ban via alternative means."
        elif result and not dm_state: #ban succeed dm fail.
            result_description = ban_info + "\n" + dm_info + "\n" + "Ban succeeded but DM failed to send."
        else: #either both fail or both succeed.
            result_description = ban_info + "\n" + dm_info

    else:
        #reason too large, ban action canceled.
        result_description = f"Unable to ban: {user.mention}, reason given is too long (above 512 characters). Please shorten ban reason."
        result = False
    #always return this.    
    return (result,result_description)
        
    