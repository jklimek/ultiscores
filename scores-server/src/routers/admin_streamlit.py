"""Admin Streamlit endpoint with basic authentication."""
import secrets
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import RedirectResponse

router = APIRouter()
security = HTTPBasic()

# Admin credentials (in production, use environment variables)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"


def verify_credentials(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    """Verify basic auth credentials."""
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = ADMIN_USERNAME.encode("utf8")
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = ADMIN_PASSWORD.encode("utf8")
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )
    
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@router.get("/admin")
async def admin_redirect(username: Annotated[str, Depends(verify_credentials)]):
    """
    Admin panel endpoint with basic authentication.
    
    Redirects to the Streamlit admin app running on port 8501.
    """
    return {
        "message": "Authenticated successfully",
        "username": username,
        "streamlit_url": "http://localhost:8501",
        "note": "Run the Streamlit app with: streamlit run admin_app.py"
    }

