from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from app.auth import has_permission
from app import models
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(prefix="/hr", tags=["HR"])

@router.get("/dashboard", name="hr_dashboard", response_class=HTMLResponse)
async def hr_dashboard(
    request: Request,
    user: models.User = Depends(has_permission(["hr"]))
):
    # Fetch necessary data for the HR dashboard
    return templates.TemplateResponse(
        "hr/dashboard.html",
        {"request": request, "user": user}
    )