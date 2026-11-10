import os
from fastapi import Header, HTTPException, status
from app.database import supabase_client, using_supabase

def require_admin(authorization: str | None = Header(default=None)) -> None:
    if not using_supabase():
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Administrator authentication is not configured.")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please sign in to continue.")
    user = supabase_client().auth.get_user(authorization.removeprefix("Bearer ")).user
    allowed = {email.strip().lower() for email in os.getenv("ADMIN_EMAILS", "").split(",") if email.strip()}
    if not user or not user.email or user.email.lower() not in allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Your account is not authorised for administration.")
