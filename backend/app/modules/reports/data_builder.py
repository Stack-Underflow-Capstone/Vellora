from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import List
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.reports.models import Report
from app.modules.trips.models import Trip
from app.modules.expenses.models import Expense


@dataclass
class TripReportItem:
    date: date
    purpose: str
    miles: float
    category_name: str
    rate_used: float | None
    mileage_total: float


@dataclass
class ExpenseReportItem:
    date: date
    type: str
    amount: float


@dataclass
class ReportData:
    employee_name: str
    employee_email: str
    period_start: date
    period_end: date
    generated_at: datetime

    trips: List[TripReportItem]
    expenses: List[ExpenseReportItem]

    total_miles: float
    total_mileage_amount: float
    total_expense_amount: float
    grand_total: float


class ReportDataBuilder:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def build(self, report: Report) -> ReportData:
        #load trips in time range for the user
        trip_result = await self.session.execute(
            sa.select(Trip)
            .options(
                selectinload(Trip.rate_category),
                selectinload(Trip.rate_customization),
                selectinload(Trip.expenses),
            )
            .where(
                Trip.user_id == report.user_id,
                Trip.started_at >= report.start_date,
                Trip.started_at <= report.end_date,
            )
        )
        trips: list[Trip] = trip_result.scalars().all()

        #load expenses linked to found trips
        trip_ids = [t.id for t in trips]

        expenses: list[Expense] = []
        if trip_ids:
            exp_result = await self.session.execute(
                sa.select(Expense)
                .options(selectinload(Expense.trip))
                .where(Expense.trip_id.in_(trip_ids))
            )
            expenses = exp_result.scalars().all()

        #convert trips into printable thingy
        trip_items: list[TripReportItem] = []
        total_miles = 0.0
        total_mileage_amount = 0.0

        for t in trips:
            miles = float(t.miles or 0)
            mileage_total = float(t.mileage_reimbursement_total or 0)

            total_miles += miles
            total_mileage_amount += mileage_total

            trip_items.append(
                TripReportItem(
                    date=t.started_at.date(),
                    purpose=t.purpose or "Unspecified",
                    miles=miles,
                    category_name=t.rate_category.name
                    if t.rate_category else "Unknown",
                    rate_used=t.reimbursement_rate,
                    mileage_total=mileage_total,
                )
            )

        #convert expenses into printable thingy
        expense_items: list[ExpenseReportItem] = []
        total_expense_amount = 0.0

        for e in expenses:
            amount = float(e.amount or 0)
            total_expense_amount += amount

            expense_items.append(
                ExpenseReportItem(
                    date=e.created_at.date(),
                    type=e.type,
                    amount=amount,
                )
            )

        user = report.user

        return ReportData(
            employee_name=user.full_name or "Unknown User",
            employee_email=user.email,
            period_start=report.start_date,
            period_end=report.end_date,
            #will make this timezone friendly later
            generated_at=datetime.now(timezone.utc),

            trips=trip_items,
            expenses=expense_items,

            total_miles=total_miles,
            total_mileage_amount=total_mileage_amount,
            total_expense_amount=total_expense_amount,
            grand_total=total_mileage_amount + total_expense_amount,
        )