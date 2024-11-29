# app/routers/users.py

from typing import Optional

from fastapi import APIRouter, Depends, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.exc import IntegrityError

from app import models, schemas
from app.crud.users import CRUDUser
from app.auth import has_permission
from fastapi.templating import Jinja2Templates
from app.database import get_db

from sqlalchemy.ext.asyncio import AsyncSession

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/edit/{user_id}", name="edit_user", response_class=HTMLResponse)
async def edit_user_form(
    request: Request,
    user_id: int,
    current_user: models.User = Depends(has_permission(["admin"])),
    db: AsyncSession = Depends(get_db)
):
    # Retrieve the user to edit using CRUDUser's get method
    user_to_edit = await CRUDUser.get(db, id=user_id)
    if not user_to_edit:
        raise HTTPException(status_code=404, detail="User not found")

    return templates.TemplateResponse(
        "users/edit_user.html",
        {
            "request": request,
            "user": current_user,
            "edit_user": user_to_edit
        }
    )


@router.post("/edit/{user_id}", name="edit_user", response_class=RedirectResponse)
async def edit_user(
    user_id: int,
    username: str = Form(...),
    email: str = Form(...),
    role: str = Form(...),
    password: Optional[str] = Form(None),
    current_user: models.User = Depends(has_permission(["admin"])),
    db: AsyncSession = Depends(get_db)
):
    # Retrieve the user to edit
    user_to_edit = await CRUDUser.get(db, id=user_id)
    if not user_to_edit:
        raise HTTPException(status_code=404, detail="User not found")

    # Prepare the update schema
    user_update = schemas.UserUpdate(
        username=username,
        email=email,
        role=role,
        password=password
    )

    try:
        # Update the user using CRUDUser's update_user method
        updated_user = await user_to_edit.update_user(db, db_obj=user_to_edit, obj_in=user_update)
        return RedirectResponse(url=router.url_path_for("view_users"), status_code=status.HTTP_303_SEE_OTHER)
    except IntegrityError:
        await db.rollback()
        error = "A user with this username or email already exists."

        return templates.TemplateResponse(
            "users/edit_user.html",
            {
                "request": Request,
                "user": current_user,
                "edit_user": user_to_edit,
                "error": error
            }
        )


@router.post("/delete/{user_id}", name="delete_user", response_class=RedirectResponse)
async def delete_user(
    user_id: int,
    current_user: models.User = Depends(has_permission(["admin"])),
    db: AsyncSession = Depends(get_db)
):
    # Retrieve the user to delete
    user_to_delete = await users.get(db, id=user_id)
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="User not found")

    # Delete the user using CRUDUser's delete_user method
    await users.delete_user(db, id=user_id)
    return RedirectResponse(url=router.url_path_for("view_users"), status_code=status.HTTP_303_SEE_OTHER)


@router.get("/", name="view_users", response_class=HTMLResponse)
async def view_users(
    request: Request,
    current_user: models.User = Depends(has_permission(["admin"])),
    db: AsyncSession = Depends(get_db)
):
    # Retrieve all users using CRUDUser's get_multi method
    users_list = await users.get_multi(db, skip=0, limit=100)  # Adjust skip and limit as needed

    return templates.TemplateResponse("users/users.html", {"request": request, "user": current_user, "users": users_list})


@router.get("/add", name="add_user", response_class=HTMLResponse)
async def create_user_form(
    request: Request,
    current_user: models.User = Depends(has_permission(["admin"])),
    db: AsyncSession = Depends(get_db)
):
    return templates.TemplateResponse("users/add_user.html", {"request": request, "user": current_user})


@router.post("/add", name="add_user", response_class=RedirectResponse)
async def create_user(
    username: str = Form(...),
    email: str = Form(...),
    role: str = Form(...),
    password: str = Form(...),
    current_user: models.User = Depends(has_permission(["admin"])),
    db: AsyncSession = Depends(get_db)
):
    user_create = schemas.UserCreate(
        username=username,
        email=email,
        role=role,
        password=password,
    )

    try:
        # Create the user using CRUDUser's create_user method
        new_user = await users.create_user(db, obj_in=user_create)
        return RedirectResponse(url=router.url_path_for("view_users"), status_code=status.HTTP_303_SEE_OTHER)
    except IntegrityError:
        await db.rollback()
        error = "A user with this username or email already exists."

        return templates.TemplateResponse(
            "users/add_user.html",
            {
                "request": Request,
                "user": current_user,
                "error": error
            }
        )
