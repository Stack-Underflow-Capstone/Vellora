from uuid import UUID
from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.expenses.models import Expense

class ExpenseRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, expense: Expense) -> Expense:
        self.db.add(expense)
        await self.db.commit()
        await self.db.refresh(expense)
        
        return expense
    
    async def get_expense(self, expense_id: UUID, user_id: UUID = None) -> Expense:
        query = select(Expense).where(Expense.id == expense_id)
        if user_id is not None:
            query = query.where(Expense.user_id == user_id)
        return await self.db.scalar(query)
    
    async def get_expenses_by_trip_id(self, trip_id: UUID, user_id: UUID = None):
        query = select(Expense).where(Expense.trip_id == trip_id)
        if user_id is not None:
            query = query.where(Expense.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_trip_and_type(
        self,
        trip_id: UUID,
        expense_type: str,
        user_id: UUID | None = None,
    ) -> Expense | None:
        normalized = expense_type.strip().lower()
        query = select(Expense).where(
            Expense.trip_id == trip_id,
            func.lower(Expense.type) == normalized,
        )
        if user_id is not None:
            query = query.where(Expense.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def delete_expense(self, expense: Expense) -> None:       
        await self.db.delete(expense)
        await self.db.commit()

    async def sum_by_trip(self, trip_id: UUID) -> float:
        result = await self.db.execute(
            select(func.sum(Expense.amount))
            .where(Expense.trip_id == trip_id)
        )
        return result.scalar() or 0.0
