# app/routers/auth.py

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import timedelta

from app import auth
from app.auth import get_current_user
from app.auth import has_permission

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(tags=["Authentication"])


@router.get("/login", response_class=HTMLResponse, name="login_page")
async def login_page(request: Request):
    """
    Renders the login form.
    """
    return templates.TemplateResponse("auth/login.html", {"request": request, "user": None})


@router.post("/login", name="login")
async def login(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
):
    """
    Authenticates the user and redirects based on their role.
    """
    user = await auth.authenticate_user(username, password)
    if not user:
        # Invalid credentials; re-render the login page with an error message
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Invalid username or password."},
            status_code=401,
        )

    # Create JWT token
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )

    # Determine redirect URL based on user role
    role_redirect_map = {
        "admin": "/admin/dashboard",
        "hr": "/hr/dashboard",
        "department": "/departments/dashboard",
    }

    redirect_url = role_redirect_map.get(user.role, "/")  # Default redirect to homepage if role not found

    # Create RedirectResponse and set the access token in cookies
    response = RedirectResponse(url=redirect_url, status_code=303)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=auth.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert minutes to seconds
        expires=auth.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        secure=True,  # Set to True in production
        samesite="lax",  # Adjust based on your needs
    )
    return response


@router.get("/logout", name="logout", response_class=RedirectResponse)
async def logout():
    """
    Logs the user out by clearing the access token cookie and redirecting to the login page.
    """
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(key="access_token")
    return response
