from pydantic import BaseModel

class FormRequest(BaseModel):
    user_id: str # discord user ID
    reason: str # user-submitted reasoning for requesting an unban

class UpdateRequest(BaseModel):
    form_id: str # form ID
    approval: bool # Approve or Deny the unban request
    approver_id: str # discord user ID of the mod issuing the approval/denial