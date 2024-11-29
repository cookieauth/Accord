# app/crud/mixins.py

from typing import List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Query

class SearchMixin:
    async def search(
        self, db: AsyncSession, *, search_term: str, fields: List[Any]
    ) -> List[Any]:
        query = select(self.model)
        for field in fields:
            query = query.where(field.ilike(f"%{search_term}%"))
        result = await db.execute(query)
        return result.scalars().all()
