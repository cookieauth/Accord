# app/crud/personnel.py

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from app.crud.base import CRUDBase
from app.crud.mixins import SearchMixin  # Assuming you have mixins as discussed
from app import models, schemas
from app.crud.utils import PaginatedResult
from app.models import PersonnelStatusEnum


class CRUDPersonnel(CRUDBase[models.Personnel, schemas.PersonnelCreate, schemas.PersonnelUpdate], SearchMixin):
    async def get_by_edipi(self, db: AsyncSession, *, edipi: str) -> Optional[models.Personnel]:
        result = await db.execute(select(self.model).where(self.model.edipi == edipi))
        return result.scalars().first()

    async def search_personnel_by_name(
        self, db: AsyncSession, *, search_term: str
    ) -> List[models.Personnel]:
        return await self.search(
            db=db,
            search_term=search_term,
            fields=[self.model.first_name, self.model.middle_name, self.model.last_name]
        )

    async def create_personnel(
        self, db: AsyncSession, *, obj_in: schemas.PersonnelCreate
    ) -> models.Personnel:
        # Check if EDIPI already exists
        existing_personnel = await self.get_by_edipi(db, edipi=obj_in.edipi)
        if existing_personnel:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="EDIPI already exists",
            )
        return await super().create(db, obj_in=obj_in)

    async def update_personnel(
        self, db: AsyncSession, *, db_obj: models.Personnel, obj_in: schemas.PersonnelUpdate
    ) -> models.Personnel:
        if obj_in.edipi:
            existing_personnel = await self.get_by_edipi(db, edipi=obj_in.edipi)
            if existing_personnel and existing_personnel.edipi != db_obj.edipi:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="EDIPI already exists",
                )
        return await super().update(db, db_obj=db_obj, obj_in=obj_in)

    async def delete_personnel(self, db: AsyncSession, *, edipi: str) -> models.Personnel:
        db_obj = await self.get_by_edipi(db, edipi=edipi)
        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Personnel not found",
            )
        return await self.remove(db, id=db_obj.edipi)

    async def filter_personnel(
            self, db: AsyncSession, *, status: Optional[PersonnelStatusEnum] = None, branch_id: Optional[int] = None
    ) -> List[models.Personnel]:
        query = select(self.model)
        if status:
            query = query.where(self.model.status == status)
        if branch_id:
            query = query.where(self.model.branch_id == branch_id)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_personnel_paginated(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> PaginatedResult[schemas.PersonnelRead]:
        total = await db.execute(select(models.Personnel).count())
        total_count = total.scalar_one()
        personnel = await self.get_multi(db=db, skip=skip, limit=limit)
        return PaginatedResult(total=total_count, items=personnel)

# Instantiate CRUDPersonnel
crud_personnel = CRUDPersonnel(models.Personnel)
