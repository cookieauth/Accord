# app/routers/personnel.py
from typing import Optional

from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app import models, crud, schemas
from app.auth import has_permission, get_current_user
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(prefix="/personnel", tags=["Personnel"])

@router.get("/", response_class=HTMLResponse)
async def personnel_list(request: Request, current_user: models.User = Depends(get_current_user)):
    async with crud.async_session() as session:
        result = await session.execute(select(models.Personnel).options(selectinload(models.Personnel.department)))
        personnel = result.scalars().all()
    return templates.TemplateResponse("personnel/personnel.html", {"request": request, "personnel": personnel, "user": current_user})



@router.post("/add")
async def add_personnel(
    request: Request,
    name: str = Form(...),
    department_id: int = Form(...),
    status: str = Form(...),
    location: str = Form(...),
    current_user: models.User = Depends(has_permission(["hr"]))
):
    async with crud.async_session() as session:
        personnel = models.Personnel(
            name=name,
            department_id=department_id,
            status=models.StatusEnum(status),
            location=location
        )
        session.add(personnel)
        await session.commit()
    return RedirectResponse(url="/personnel", status_code=302)

@router.get("/edit/{personnel_id}", name="edit_personnel", response_class=HTMLResponse)
async def edit_personnel_form(
    request: Request,
    personnel_id: int,
    current_user: models.User = Depends(has_permission(["admin"]))
):
    async with crud.async_session() as session:
        result = await session.execute(
            select(models.Personnel)
            .options(selectinload(models.Personnel.department))
            .where(models.Personnel.id == personnel_id)
        )
        personnel = result.scalar_one_or_none()
        if not personnel:
            raise HTTPException(status_code=404, detail="Personnel not found")
        departments = (await session.execute(select(models.Department))).scalars().all()
    return templates.TemplateResponse(
        "personnel/edit_personnel.html",
        {"request": request, "user": current_user, "personnel": personnel, "departments": departments}
    )


@router.post("/edit/{personnel_id}", name="edit_personnel")
async def edit_personnel(
    request: Request,
    personnel_id: int,
    name: str = Form(...),
    department_id: int = Form(...),
    status: schemas.StatusEnum = Form(...),
    location: Optional[str] = Form(None),
    current_user: models.User = Depends(has_permission(["admin"]))
):
    async with crud.async_session() as session:
        result = await session.execute(
            select(models.Personnel).where(models.Personnel.id == personnel_id)
        )
        personnel = result.scalar_one_or_none()
        if not personnel:
            raise HTTPException(status_code=404, detail="Personnel not found")
        personnel.name = name
        personnel.department_id = department_id
        personnel.status = status
        personnel.location = location
        await session.commit()
    return RedirectResponse(
        url=router.url_path_for("view_personnel"), status_code=303
    )

@router.delete("/delete/{personnel_id}", name="delete_personnel")
async def delete_personnel(
    personnel_id: int,
    current_user: models.User = Depends(has_permission(["admin"]))
):
    async with crud.async_session() as session:
        result = await session.execute(
            select(models.Personnel).where(models.Personnel.id == personnel_id)
        )
        personnel = result.scalar_one_or_none()
        if not personnel:
            raise HTTPException(status_code=404, detail="Personnel not found")
        await session.delete(personnel)
        await session.commit()
    return RedirectResponse(
        url=router.url_path_for("view_personnel"), status_code=303
    )

@router.get("/personnel", name="view_personnel", response_class=HTMLResponse)
async def view_personnel(request: Request, current_user: models.User = Depends(has_permission(["admin"]))):
    async with crud.async_session() as session:
        result = await session.execute(select(models.Personnel).options(selectinload(models.Personnel.department)))
        personnel = result.scalars().all()
    return templates.TemplateResponse("personnel/personnel.html", {"request": request, "user": current_user, "personnel": personnel})

@router.get("/personnel/add", name="add_personnel", response_class=HTMLResponse)
async def add_personnel_form(request: Request, user: models.User = Depends(has_permission(["admin"]))):
    # Fetch departments to populate a dropdown
    async with crud.async_session() as session:
        result = await session.execute(select(models.Department))
        departments = result.scalars().all()
    return templates.TemplateResponse("personnel/add_personnel.html", {"request": request, "user": user, "departments": departments})

@router.post("/personnel/add", name="add_personnel", response_class=HTMLResponse)
async def add_personnel(
    request: Request,
    name: str = Form(...),
    department_id: int = Form(...),
    status: schemas.StatusEnum = Form(...),
    location: Optional[str] = Form(None),
    user: models.User = Depends(has_permission(["admin"]))
):
    new_personnel = models.Personnel(
        name=name,
        department_id=department_id,
        status=status,
        location=location
    )
    async with crud.async_session() as session:
        session.add(new_personnel)
        try:
            await session.commit()
            await session.refresh(new_personnel)
            return RedirectResponse(url=router.url_path_for("view_personnel"), status_code=303)
        except Exception as e:
            await session.rollback()
            error = f"An error occurred: {str(e)}"
            # Fetch departments again for the form
            result = await session.execute(select(models.Department))
            departments = result.scalars().all()
            return templates.TemplateResponse(
                "personnel/add_personnel.html",
                {"request": request, "user": user, "error": error, "departments": departments}
            )