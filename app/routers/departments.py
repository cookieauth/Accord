# app/routers/departments.py

from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app import models, crud
from app.auth import has_permission, get_current_user

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(prefix="/departments", tags=["Departments"])

@router.get("/dashboard", name="department_dashboard", response_class=HTMLResponse)
async def department_dashboard(
        request: Request,
        user: models.User = Depends(has_permission("department"))
):
    # Ensure the user has an associated department
    if not user.department:
        raise HTTPException(status_code=400, detail="User is not assigned to any department.")

    async with crud.async_session() as session:
        # Fetch personnel in the user's department
        personnel = (await session.execute(
            select(models.Personnel)
            .where(models.Personnel.department_id == user.department.id)
            .options(selectinload(models.Personnel.department))
        )).scalars().all()

        # Calculate statistics
        total_personnel = len(personnel)
        active_personnel = len([p for p in personnel if p.status == 'ACTIVE'])

    return templates.TemplateResponse(
        "departments/dashboard.html",
        {
            "request": request,
            "user": user,
            "personnel": personnel,
            "total_personnel": total_personnel,
            "active_personnel": active_personnel
        }
    )

@router.get("/add", response_class=HTMLResponse)
async def add_department_form(request: Request, current_user: models.User = Depends(has_permission(["admin"]))):
    return templates.TemplateResponse("departments/add_department.html", {"request": request})

@router.post("/add", name="create_department")
async def create_department(request: Request, name: str = Form(...), user: models.User = Depends(has_permission(["admin"]))):
    new_department = models.Department(name=name)
    async with crud.async_session() as session:
        session.add(new_department)
        try:
            await session.commit()
            await session.refresh(new_department)
            return RedirectResponse(url=router.url_path_for("view_departments"), status_code=303)
        except IntegrityError:
            await session.rollback()
            error = "A department with this name already exists."
            return templates.TemplateResponse("departments/add_department.html", {"request": request, "user": user, "error": error})


@router.delete("/delete/{department_id}", name="delete_department")
async def delete_department(
    department_id: int,
    user: models.User = Depends(has_permission(["admin"]))
):
    async with crud.async_session() as session:
        result = await session.execute(
            select(models.Department).where(models.Department.id == department_id)
        )
        department = result.scalar_one_or_none()
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")
        await session.delete(department)
        await session.commit()
    return RedirectResponse(
        url=router.url_path_for("view_departments"), status_code=303
    )
@router.get("/edit/{department_id}", name="edit_department", response_class=HTMLResponse)
async def edit_department_form(
    request: Request,
    department_id: int,
    user: models.User = Depends(has_permission(["admin"]))
):
    async with crud.async_session() as session:
        result = await session.execute(
            select(models.Department).where(models.Department.id == department_id)
        )
        department = result.scalar_one_or_none()
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")
    return templates.TemplateResponse(
        "departments/edit_department.html",
        {"request": request, "user": user, "department": department}
    )

@router.post("/edit/{department_id}", name="edit_department")
async def edit_department(
    request: Request,
    department_id: int,
    name: str = Form(...),
    user: models.User = Depends(has_permission(["admin"]))
):
    async with crud.async_session() as session:
        try:
            result = await session.execute(
                select(models.Department).where(models.Department.id == department_id)
            )
            department = result.scalar_one_or_none()
            if not department:
                raise HTTPException(status_code=404, detail="Department not found")
            department.name = name
            await session.commit()
            return RedirectResponse(
                url=router.url_path_for("view_departments"), status_code=303
            )
        except IntegrityError:
            await session.rollback()
            error = "A department with this name already exists."
            return templates.TemplateResponse(
                "departments/edit_department.html",
                {"request": request, "user": user, "department": department, "error": error}
            )

@router.get("/departments", name="view_departments", response_class=HTMLResponse)
async def view_departments(request: Request, current_user: models.User = Depends(has_permission(["admin"]))):
    async with crud.async_session() as session:
        result = await session.execute(select(models.Department))
        departments = result.scalars().all()
    return templates.TemplateResponse("admin/departments.html", {"request": request, "user": current_user, "departments": departments})