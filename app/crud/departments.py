# app/crud/departments.py
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from app.crud.base import CRUDBase, ModelType
from app import models, schemas

class CRUDDepartment(CRUDBase[models.Department, schemas.DepartmentCreate, schemas.DepartmentUpdate]):
    async def create_department(
        self, db: AsyncSession, *, obj_in: schemas.DepartmentCreate
    ) -> models.Department:
        # Check if department name already exists
        existing_department = await self.get_by_name(db, name=obj_in.name)
        if existing_department:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Department name already exists",
            )
        return await super().create(db, obj_in=obj_in)

    async def get_by_name(self, db: AsyncSession, *, name: str) -> Optional[models.Department]:
        result = await db.execute(select(self.model).where(self.model.name == name))
        return result.scalars().first()

    async def update_department(
        self, db: AsyncSession, *, db_obj: models.Department, obj_in: schemas.DepartmentUpdate
    ) -> models.Department:
        if obj_in.name:
            existing_department = await self.get_by_name(db, name=obj_in.name)
            if existing_department and existing_department.id != db_obj.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Department name already exists",
                )
        return await super().update(db, db_obj=db_obj, obj_in=obj_in)

    async def delete_department(self, db: AsyncSession, *, id: int) -> models.Department:
        return await super().remove(db, id=id)


# Instantiate CRUDDepartment
crud_department = CRUDDepartment(models.Department)
