from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.expenses.models import ExpenseReceipt


class ExpenseReceiptRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, receipt: ExpenseReceipt) -> ExpenseReceipt:
        self.db.add(receipt)
        await self.db.commit()
        await self.db.refresh(receipt)
        return receipt

    async def list_for_trip(self, trip_id: UUID, user_id: UUID | None = None) -> list[ExpenseReceipt]:
        query = select(ExpenseReceipt).where(ExpenseReceipt.trip_id == trip_id)
        if user_id is not None:
            query = query.where(ExpenseReceipt.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get(self, receipt_id: UUID, user_id: UUID | None = None) -> ExpenseReceipt | None:
        query = select(ExpenseReceipt).where(ExpenseReceipt.id == receipt_id).options(
            selectinload(ExpenseReceipt.trip)
        )
        if user_id is not None:
            query = query.where(ExpenseReceipt.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def delete(self, receipt: ExpenseReceipt) -> None:
        await self.db.delete(receipt)
        await self.db.commit()
