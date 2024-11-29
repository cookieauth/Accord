# app/crud/users.py

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from app.crud.base import CRUDBase
from app import models, schemas

class CRUDUser(CRUDBase[models.User, schemas.UserCreate, schemas.UserUpdate]):
    async def get_by_username(self, db: AsyncSession, *, username: str) -> Optional[models.User]:
        result = await db.execute(select(self.model).where(self.model.username == username))
        return result.scalars().first()

    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[models.User]:
        result = await db.execute(select(self.model).where(self.model.email == email))
        return result.scalars().first()

    async def create_user(self, db: AsyncSession, *, obj_in: schemas.UserCreate) -> models.User:
        # Check for existing username
        existing_user = await self.get_by_username(db, username=obj_in.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )
        # Check for existing email
        if obj_in.email:
            existing_email = await self.get_by_email(db, email=obj_in.email)
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered",
                )
        return await super().create(db, obj_in=obj_in)

    async def update_user(
        self, db: AsyncSession, db_obj: models.User, obj_in: schemas.UserUpdate
    ) -> models.User:
        if obj_in.email:
            existing_email = await self.get_by_email(db, email=obj_in.email)
            if existing_email and existing_email.user_id != db_obj.user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered",
                )
        return await super().update(db, db_obj=db_obj, obj_in=obj_in)

    async def delete_user(self, db: AsyncSession, *, user_id: int) -> models.User:
        return await super().remove(db, id=user_id)

# Instantiate CRUDUser
crud_user = CRUDUser(models.User)
