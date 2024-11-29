# app/routers/notifications.py

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from starlette.exceptions import HTTPException
from starlette.responses import RedirectResponse

from app.auth import has_permission
from app import models, crud
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/", name="view_notifications", response_class=HTMLResponse)
async def view_notifications(
    request: Request,
    user: models.User = Depends(has_permission(["admin", "hr", "department"]))
):
    async with crud.async_session() as session:
        notifications = (await session.execute(
            select(models.Notification)
            .where(models.Notification.user_id == user.id)
            .order_by(models.Notification.created_at.desc())
        )).scalars().all()
        # Optionally, mark all as read when viewed
        for notification in notifications:
            if not notification.is_read:
                notification.is_read = True
        await session.commit()
    # Calculate unread notifications count for base.html
    unread_count = len([n for n in user.notifications if not n.is_read])
    return templates.TemplateResponse(
        "notifications/notifications.html",
        {
            "request": request,
            "user": user,
            "notifications": notifications,
            "unread_count": unread_count
        }
    )

@router.post("/mark_as_read/{notification_id}", name="mark_notification_as_read")
async def mark_notification_as_read(
    notification_id: int,
    user: models.User = Depends(has_permission(["admin", "hr", "department"]))
):
    async with crud.async_session() as session:
        notification = (await session.execute(
            select(models.Notification).where(models.Notification.id == notification_id, models.Notification.user_id == user.id)
        )).scalar_one_or_none()
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        notification.is_read = True
        await session.commit()
    return RedirectResponse(url=router.url_path_for("view_notifications"), status_code=303)

@router.post("/mark_as_unread/{notification_id}", name="mark_notification_as_unread")
async def mark_notification_as_unread(
    notification_id: int,
    user: models.User = Depends(has_permission(["admin", "hr", "department"]))
):
    async with crud.async_session() as session:
        notification = (await session.execute(
            select(models.Notification).where(models.Notification.id == notification_id, models.Notification.user_id == user.id)
        )).scalar_one_or_none()
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        notification.is_read = False
        await session.commit()
    return RedirectResponse(url=router.url_path_for("view_notifications"), status_code=303)

@router.post("/delete/{notification_id}", name="delete_notification")
async def delete_notification(
    notification_id: int,
    user: models.User = Depends(has_permission(["admin", "hr", "department"]))
):
    async with crud.async_session() as session:
        notification = (await session.execute(
            select(models.Notification).where(models.Notification.id == notification_id, models.Notification.user_id == user.id)
        )).scalar_one_or_none()
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        await session.delete(notification)
        await session.commit()
    return RedirectResponse(url=router.url_path_for("view_notifications"), status_code=303)