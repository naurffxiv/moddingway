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
) -> Optional[Tuple[bool, bool, str]]:
    """Executes ban of user

    Args:
        user (discord.Member): mention or "@"/user ID of the user being banned.
        reason (str): description of ban reason.

    Returns:
        Optional[Tuple[bool, bool, str]]: tuple containing (result,dm_state,result_description)
            - result (bool): Indicates whether the ban succeeded.
            - dm_state (bool): Indicates whether the DM notification to the user succeeded.
            - result_description (str): A message describing the status of the ban operation.
    """
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
            logger.info(f"Successfully sent dm to {user.mention}")
            dm_state = True
        except discord.Forbidden as e:
            logger.error(f"DM to {user.mention} failed due to permission error: {e}")
            dm_state = False
        except discord.HTTPException as e:
            logger.error(f"DM to {user.mention} due to HTTP Error: {e}")
            dm_state = False
        except Exception as e:
            logger.error(f"DM to {user.mention} due to Unknown Error: {e}")
            dm_state = False

        #attempt Ban
        try:
            await user.ban(reason=reason)
            logger.info(f"Successfully banned {user.mention}")
            result = True
        except discord.Forbidden as e:
            logger.error(f"Ban of {user.mention} failed due to permission error: {e}")
            result = False
        except discord.HTTPException as e:
            logger.error(f"Ban of {user.mention} failed due to HTTP Error: {e}")
            result = False
        except Exception as e:
            logger.error(f"Ban of {user.mention} failed due to Unknown Error: {e}")
            result = False
    
        if not result and dm_state: #ban fail dm succeed.
            result_description =  f"Unable to ban {user.mention}, please ban via discord built-in ban feature. A DM has been sent to {user.mention} with ban reason."
        elif result and not dm_state: #ban succeed dm fail.
            result_description = f"Successfully banned {user.mention} but DM failed to send."
        elif result and dm_state: #full success
            result_description = f"Successfully banned {user.mention} and DM has been sent with ban reason."
        else: #full failure
            result_description = f"Unable to ban {user.mention} and unable to send DM. Please ban via discord built-in ban feature or try again later."

    else:
        #reason too large, ban action canceled.
        result_description = f"Unable to ban: {user.mention}, reason given is too long (above 512 characters). Please shorten ban reason."
        result = False
    #always return this.    
    return (result,dm_state,result_description)
        
    