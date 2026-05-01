import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.modules.expenses.service import ExpensesService
from app.modules.expenses.repository import ExpenseRepo
from app.modules.trips.repository import TripRepo
from app.modules.expenses.schemas import CreateExpenseDTO, EditExpenseDTO
from app.modules.expenses.models import Expense
from app.modules.trips.models import Trip
from app.modules.expenses.exceptions import (
    ExpenseNotFoundError,
    DuplicateExpenseError
)
from app.modules.trips.exceptions import TripNotFoundError


class TestExpensesServiceCreateExpense:

    @pytest.fixture
    def user_id(self):
        return uuid4()

    @pytest.fixture
    def expense_repo(self):
        return AsyncMock(spec=ExpenseRepo)

    @pytest.fixture
    def trip_repo(self):
        return AsyncMock(spec=TripRepo)

    @pytest.fixture
    def service(self, expense_repo, trip_repo):
        return ExpensesService(expense_repo, trip_repo)

    @pytest.fixture
    def mock_trip(self):
        trip = MagicMock(spec=Trip)
        trip.id = uuid4()
        trip.expense_reimbursement_total = 0.0
        return trip

    @pytest.fixture
    def mock_expense(self):
        expense = MagicMock(spec=Expense)
        expense.id = uuid4()
        expense.trip_id = uuid4()
        expense.type = "Parking"
        expense.amount = 15.50
        return expense

    @pytest.mark.asyncio
    async def test_create_expense_success(
        self, service, expense_repo, trip_repo, mock_trip, mock_expense, user_id
    ):
        trip_id = uuid4()
        dto = CreateExpenseDTO(type="Parking", amount=15.50)
        trip_repo.get.return_value = mock_trip
        expense_repo.get_by_trip_and_type.return_value = None
        expense_repo.save.return_value = mock_expense
        expense_repo.sum_by_trip.return_value = 15.50

        with patch('app.modules.expenses.service.Expense') as MockExpense:
            MockExpense.return_value = mock_expense
            result = await service.create_expense(user_id, trip_id, dto)

        assert result == mock_expense
        expense_repo.save.assert_called()

    @pytest.mark.asyncio
    async def test_create_expense_trip_not_found(self, service, trip_repo, user_id):
        trip_id = uuid4()
        dto = CreateExpenseDTO(type="Parking", amount=15.50)
        trip_repo.get.return_value = None

        with pytest.raises(TripNotFoundError):
            await service.create_expense(user_id, trip_id, dto)

    @pytest.mark.asyncio
    async def test_create_expense_duplicate_type(
        self, service, expense_repo, trip_repo, mock_trip, mock_expense, user_id
    ):
        trip_id = uuid4()
        dto = CreateExpenseDTO(type="Parking", amount=15.50)
        trip_repo.get.return_value = mock_trip
        expense_repo.get_by_trip_and_type.return_value = mock_expense

        with pytest.raises(DuplicateExpenseError):
            await service.create_expense(user_id, trip_id, dto)


class TestExpensesServiceGetExpensesForTrip:

    @pytest.fixture
    def expense_repo(self):
        return AsyncMock(spec=ExpenseRepo)

    @pytest.fixture
    def trip_repo(self):
        return AsyncMock(spec=TripRepo)

    @pytest.fixture
    def service(self, expense_repo, trip_repo):
        return ExpensesService(expense_repo, trip_repo)

    @pytest.fixture
    def mock_trip(self):
        trip = MagicMock(spec=Trip)
        trip.id = uuid4()
        return trip

    @pytest.fixture
    def user_id(self):
        return uuid4()

    @pytest.mark.asyncio
    async def test_get_expenses_for_trip_success(
        self, service, expense_repo, trip_repo, mock_trip, user_id
    ):
        trip_id = uuid4()
        mock_expenses = [MagicMock(spec=Expense), MagicMock(spec=Expense)]
        trip_repo.get.return_value = mock_trip
        expense_repo.get_expenses_by_trip_id.return_value = mock_expenses

        result = await service.get_expenses_for_trip(user_id, trip_id)

        assert result == mock_expenses
        expense_repo.get_expenses_by_trip_id.assert_called_once_with(trip_id, user_id)

    @pytest.mark.asyncio
    async def test_get_expenses_for_trip_trip_not_found(self, service, trip_repo, user_id):
        trip_id = uuid4()
        trip_repo.get.return_value = None

        with pytest.raises(TripNotFoundError):
            await service.get_expenses_for_trip(user_id, trip_id)


class TestExpensesServiceGetExpense:

    @pytest.fixture
    def expense_repo(self):
        return AsyncMock(spec=ExpenseRepo)

    @pytest.fixture
    def trip_repo(self):
        return AsyncMock(spec=TripRepo)

    @pytest.fixture
    def service(self, expense_repo, trip_repo):
        return ExpensesService(expense_repo, trip_repo)

    @pytest.fixture
    def user_id(self):
        return uuid4()

    @pytest.mark.asyncio
    async def test_get_expense_success(self, service, expense_repo, user_id):
        expense_id = uuid4()
        mock_expense = MagicMock(spec=Expense)
        expense_repo.get_expense.return_value = mock_expense

        result = await service.get_expense(user_id, expense_id)

        assert result == mock_expense
        expense_repo.get_expense.assert_called_once_with(expense_id, user_id)

    @pytest.mark.asyncio
    async def test_get_expense_not_found(self, service, expense_repo, user_id):
        expense_id = uuid4()
        expense_repo.get_expense.return_value = None

        with pytest.raises(ExpenseNotFoundError):
            await service.get_expense(user_id, expense_id)


class TestExpensesServiceEditExpense:

    @pytest.fixture
    def expense_repo(self):
        return AsyncMock(spec=ExpenseRepo)

    @pytest.fixture
    def trip_repo(self):
        return AsyncMock(spec=TripRepo)

    @pytest.fixture
    def service(self, expense_repo, trip_repo):
        return ExpensesService(expense_repo, trip_repo)

    @pytest.fixture
    def mock_expense(self):
        expense = MagicMock(spec=Expense)
        expense.id = uuid4()
        expense.trip_id = uuid4()
        expense.type = "Parking"
        expense.amount = 15.50
        return expense

    @pytest.fixture
    def mock_trip(self):
        trip = MagicMock(spec=Trip)
        trip.id = uuid4()
        trip.expense_reimbursement_total = 0.0
        return trip

    @pytest.fixture
    def user_id(self):
        return uuid4()

    @pytest.mark.asyncio
    async def test_edit_expense_success(
        self, service, expense_repo, trip_repo, mock_expense, mock_trip, user_id
    ):
        expense_id = uuid4()
        dto = EditExpenseDTO(type="Tolls", amount=25.00)
        expense_repo.get_expense.return_value = mock_expense
        trip_repo.get.return_value = mock_trip
        expense_repo.get_by_trip_and_type.return_value = None
        expense_repo.save.return_value = mock_expense
        expense_repo.sum_by_trip.return_value = 25.00

        result = await service.edit_expense(user_id, expense_id, dto)

        assert result == mock_expense
        expense_repo.save.assert_called()

    @pytest.mark.asyncio
    async def test_edit_expense_not_found(self, service, expense_repo, user_id):
        expense_id = uuid4()
        dto = EditExpenseDTO(type="Tolls")
        expense_repo.get_expense.return_value = None

        with pytest.raises(ExpenseNotFoundError):
            await service.edit_expense(user_id, expense_id, dto)

    @pytest.mark.asyncio
    async def test_edit_expense_duplicate_type(
        self, service, expense_repo, mock_expense, user_id
    ):
        expense_id = uuid4()
        dto = EditExpenseDTO(type="Tolls")
        other_expense = MagicMock(spec=Expense)
        other_expense.id = uuid4()
        
        expense_repo.get_expense.return_value = mock_expense
        expense_repo.get_by_trip_and_type.return_value = other_expense

        with pytest.raises(DuplicateExpenseError):
            await service.edit_expense(user_id, expense_id, dto)

    @pytest.mark.asyncio
    async def test_edit_expense_no_changes(self, service, expense_repo, mock_expense, user_id):
        expense_id = uuid4()
        dto = EditExpenseDTO()
        expense_repo.get_expense.return_value = mock_expense
        expense_repo.save.return_value = mock_expense

        result = await service.edit_expense(user_id, expense_id, dto)

        assert result == mock_expense
        expense_repo.save.assert_called()


class TestExpensesServiceDeleteExpense:

    @pytest.fixture
    def expense_repo(self):
        return AsyncMock(spec=ExpenseRepo)

    @pytest.fixture
    def trip_repo(self):
        return AsyncMock(spec=TripRepo)

    @pytest.fixture
    def service(self, expense_repo, trip_repo):
        return ExpensesService(expense_repo, trip_repo)

    @pytest.fixture
    def mock_expense(self):
        expense = MagicMock(spec=Expense)
        expense.id = uuid4()
        expense.trip_id = uuid4()
        return expense

    @pytest.fixture
    def mock_trip(self):
        trip = MagicMock(spec=Trip)
        trip.id = uuid4()
        trip.expense_reimbursement_total = 50.0
        return trip

    @pytest.fixture
    def user_id(self):
        return uuid4()

    @pytest.mark.asyncio
    async def test_delete_expense_success(
        self, service, expense_repo, trip_repo, mock_expense, mock_trip, user_id
    ):
        expense_id = uuid4()
        expense_repo.get_expense.return_value = mock_expense
        trip_repo.get.return_value = mock_trip
        expense_repo.sum_by_trip.return_value = 35.00

        await service.delete_expense(user_id, expense_id)

        expense_repo.delete_expense.assert_called_once_with(mock_expense)

    @pytest.mark.asyncio
    async def test_delete_expense_not_found(self, service, expense_repo, user_id):
        expense_id = uuid4()
        expense_repo.get_expense.return_value = None

        with pytest.raises(ExpenseNotFoundError):
            await service.delete_expense(user_id, expense_id)
