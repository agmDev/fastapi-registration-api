from pydantic import BaseModel, Field

class ActivateAccountRequest(BaseModel):
    code: str = Field(
        pattern=r"^\d{4}$",
        description="4 digits activation code"
    )


class ActivateAccountResponse(BaseModel):
    message: str = "Account successfully activated."