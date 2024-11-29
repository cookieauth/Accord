# app/routers/admin.py
from typing import Optional

from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app import models, schemas, crud, auth
from app.auth import has_permission

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/dashboard", name="admin_dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, current_user: models.User = Depends(has_permission(["admin"]))):
    async with crud.async_session() as session:
        user_count_result = await session.execute(select(func.count(models.User.id)))
        user_count = user_count_result.scalar()

        department_count_result = await session.execute(select(func.count(models.Department.id)))
        department_count = department_count_result.scalar()

        personnel_count_result = await session.execute(select(func.count(models.Personnel.id)))
        personnel_count = personnel_count_result.scalar()

        muster_report_count_result = await session.execute(select(func.count(models.MusterReport.id)))
        muster_report_count = muster_report_count_result.scalar()

    dashboard_data = {
        "user_count": user_count,
        "department_count": department_count,
        "personnel_count": personnel_count,
        "muster_report_count": muster_report_count,
    }

    unread_count = len([n for n in current_user.notifications if not n.is_read])

    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "user": current_user,
            "dashboard_data": dashboard_data,
            "unread_count": unread_count,
        })
