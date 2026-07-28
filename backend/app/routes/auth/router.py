import secrets

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str = ""
    password: str = ""


@router.post("/login")
async def login(_req: LoginRequest):
    return {
        "token": secrets.token_hex(32),
        "user": {
            "name": "User",
            "roles": ["user", "admin"],
            "defaultTheme": "dark",
        },
    }
