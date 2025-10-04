from fastapi_pagination import Page
import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import discord
import logging
from moddingway.settings import get_settings
from moddingway_api.utils.paginate import parse_pagination_params, paginate
from moddingway.database import banforms_database, users_database
from moddingway.database.models import BanForm
from moddingway.util import get_log_channel, create_interaction_embed_context
from moddingway_api.schemas.ban_form_schema import FormRequest, UpdateRequest
from moddingway_api.routes.banneduser_routes import unban_user


router = APIRouter(prefix="/banforms")
settings = get_settings()
authHeader = {"Authorization": f"Bot {settings.discord_token}"}
logger = logging.getLogger(__name__)


@router.get("")
async def get_ban_forms() -> Page[BanForm]:

    page, size = parse_pagination_params()
    limit = size
    offset = (page - 1) * size

    db_form_list = banforms_database.get_ban_forms(limit, offset)
    total_count = banforms_database.get_form_count()

    return paginate(db_form_list, length_function=lambda _: total_count)


@router.get("/{form_id}")
async def get_ban_form_by_id(form_id: int) -> Optional[BanForm]:

    db_form = banforms_database.get_ban_form(form_id)

    if not db_form:
        raise HTTPException(status_code=404, detail="Form not found")

    form = BanForm(
        form_id=db_form.form_id,
        user_id=db_form.user_id,
        reason=db_form.reason,
        approval=db_form.approval,
        approved_by=db_form.approved_by,
        submission_timestamp=db_form.submission_timestamp,
    )
    return form


@router.post("")
async def submit_form(request: FormRequest):

    db_user = users_database.get_user(request.user_id)

    if db_user:
        if not db_user.is_banned:
            return {"detail": f"User {request.user_id} is not currently banned"}

        form = BanForm(
            user_id=db_user.user_id,
            reason=request.reason,
            submission_timestamp=datetime.now(timezone.utc),
        )

        result = banforms_database.add_form(form)

        if result:
            # TODO: logging to moddingway
            return {"detail": f"User {request.user_id}'s form has been submitted"}

        return {
            "detail": "There was an issue with the form submission, please try again"
        }


@router.patch("")
async def update_form(request: UpdateRequest):

    db_form = banforms_database.get_ban_form(request.form_id)
    if not db_form:
        raise HTTPException(status_code=404, detail="Form not found")

    result = banforms_database.update_form(
        request.form_id, request.approval, request.approver_id
    )
    if result[0] == True:
        db_user = banforms_database.get_user_from_form(result[1])
        try:
            unban_user(db_user)
        except Exception as e:
            logger.error(f"Error unbanning user {db_user} via banform approval: {e}")

    return {"detail": f"Form {request.form_id} has been updated"}
