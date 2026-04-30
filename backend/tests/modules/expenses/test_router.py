import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from fastapi import status, HTTPException

from app.modules.expenses.router import router, get_expenses_service
from app.modules.expenses.service import ExpensesService
from app.modules.expenses.schemas import CreateExpenseDTO, EditExpenseDTO, ExpenseResponseDTO
from app.modules.expenses.models import Expense
from app.modules.expenses.exceptions import (
    ExpenseNotFoundError,
    InvalidExpenseDataError,
    DuplicateExpenseError,
)
from app.modules.trips.exceptions import TripNotFoundError
from app.modules.users.models import User, UserRole


class TestCreateExpenseEndpoint:
    """POST /trips/{trip_id}/expenses endpoint"""

    @pytest.fixture
    def mock_user(self):
        user = MagicMock(spec=User)
        user.id = uuid4()
        user.email = "test@example.com"
        user.role = UserRole.EMPLOYEE
        return user

    @pytest.fixture
    def mock_service(self):
        return AsyncMock(spec=ExpensesService)

    @pytest.fixture
    def mock_expense(self):
        expense = MagicMock(spec=Expense)
        expense.id = uuid4()
        expense.trip_id = uuid4()
        expense.type = "Parking"
        expense.amount = 1500.0
        expense.user_id = uuid4()
        return expense

    @pytest.mark.asyncio
    async def test_create_expense_success(self, mock_service, mock_expense, mock_user):

        trip_id = uuid4()
        request_body = {"type": "Parking", "amount": 1500.0}
        mock_service.create_expense.return_value = mock_expense

        from app.modules.expenses.router import create_expense
        
        result = await create_expense(
            trip_id=trip_id,
            body=CreateExpenseDTO(**request_body),
            svc=mock_service,
            current_user=mock_user
        )

        assert result == mock_expense
        mock_service.create_expense.assert_called_once_with(mock_user.id, trip_id, CreateExpenseDTO(**request_body))

    @pytest.mark.asyncio
    async def test_create_expense_trip_not_found(self, mock_service, mock_user):

        trip_id = uuid4()
        request_body = {"type": "Parking", "amount": 1500.0}
        mock_service.create_expense.side_effect = TripNotFoundError("Trip not found")

        from app.modules.expenses.router import create_expense

        with pytest.raises(HTTPException) as exc_info:
            await create_expense(
                trip_id=trip_id,
                body=CreateExpenseDTO(**request_body),
                svc=mock_service,
                current_user=mock_user
            )
        
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_create_expense_invalid_data(self, mock_service, mock_user):

        trip_id = uuid4()
        request_body = {"type": "", "amount": 1500.0}
        mock_service.create_expense.side_effect = InvalidExpenseDataError("Type is required")

        from app.modules.expenses.router import create_expense

        with pytest.raises(HTTPException) as exc_info:
            await create_expense(
                trip_id=trip_id,
                body=CreateExpenseDTO(**request_body),
                svc=mock_service,
                current_user=mock_user
            )
        
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_create_expense_duplicate(self, mock_service, mock_user):
        trip_id = uuid4()
        request_body = {"type": "Parking", "amount": 1500.0}
        mock_service.create_expense.side_effect = DuplicateExpenseError(
            "An expense with this type already exists"
        )

        from app.modules.expenses.router import create_expense

        with pytest.raises(HTTPException) as exc_info:
            await create_expense(
                trip_id=trip_id,
                body=CreateExpenseDTO(**request_body),
                svc=mock_service,
                current_user=mock_user
            )
        
        assert exc_info.value.status_code == 409


class TestGetExpensesEndpoint:
    """GET /trips/{trip_id}/expenses endpoint"""

    @pytest.fixture
    def mock_user(self):
        user = MagicMock(spec=User)
        user.id = uuid4()
        user.email = "test@example.com"
        user.role = UserRole.EMPLOYEE
        return user

    @pytest.fixture
    def mock_service(self):
        return AsyncMock(spec=ExpensesService)

    @pytest.fixture
    def mock_expenses(self):
        expenses = []
        for i in range(3):
            expense = MagicMock(spec=Expense)
            expense.id = uuid4()
            expense.type = f"Type{i}"
            expense.amount = 1000.0 * (i + 1)
            expenses.append(expense)
        return expenses

    @pytest.mark.asyncio
    async def test_get_expenses_success(self, mock_service, mock_expenses, mock_user):

        trip_id = uuid4()
        mock_service.get_expenses_for_trip.return_value = mock_expenses

        from app.modules.expenses.router import get_expenses

        result = await get_expenses(trip_id=trip_id, svc=mock_service, current_user=mock_user)

        assert result == mock_expenses
        assert len(result) == 3
        mock_service.get_expenses_for_trip.assert_called_once_with(mock_user.id, trip_id)

    @pytest.mark.asyncio
    async def test_get_expenses_empty_list(self, mock_service, mock_user):

        trip_id = uuid4()
        mock_service.get_expenses_for_trip.return_value = []

        from app.modules.expenses.router import get_expenses

        result = await get_expenses(trip_id=trip_id, svc=mock_service, current_user=mock_user)

        assert result == []

    @pytest.mark.asyncio
    async def test_get_expenses_trip_not_found(self, mock_service, mock_user):

        trip_id = uuid4()
        mock_service.get_expenses_for_trip.side_effect = TripNotFoundError("Trip not found")

        from app.modules.expenses.router import get_expenses

        with pytest.raises(HTTPException) as exc_info:
            await get_expenses(trip_id=trip_id, svc=mock_service, current_user=mock_user)
        
        assert exc_info.value.status_code == 404


class TestGetExpenseEndpoint:
    """GET /trips/{trip_id}/expenses/{expense_id} endpoint"""

    @pytest.fixture
    def mock_user(self):
        user = MagicMock(spec=User)
        user.id = uuid4()
        user.email = "test@example.com"
        user.role = UserRole.EMPLOYEE
        return user

    @pytest.fixture
    def mock_service(self):
        user = MagicMock(spec=User)
        user.id = uuid4()
        user.email = "test@example.com"
        user.role = UserRole.EMPLOYEE
        return user

    @pytest.fixture
    def mock_service(self):
        return AsyncMock(spec=ExpensesService)

    @pytest.fixture
    def mock_expense(self):
        expense = MagicMock(spec=Expense)
        expense.id = uuid4()
        expense.trip_id = uuid4()
        expense.type = "Parking"
        expense.amount = 1500.0
        return expense

    @pytest.mark.asyncio
    async def test_get_expense_success(self, mock_service, mock_expense, mock_user):

        expense_id = uuid4()
        mock_service.get_expense.return_value = mock_expense

        from app.modules.expenses.router import get_expense

        result = await get_expense(expense_id=expense_id, svc=mock_service, current_user=mock_user)

        assert result == mock_expense
        mock_service.get_expense.assert_called_once_with(mock_user.id, expense_id)

    @pytest.mark.asyncio
    async def test_get_expense_not_found(self, mock_service, mock_user):

        expense_id = uuid4()
        mock_service.get_expense.side_effect = ExpenseNotFoundError("Expense not found")

        from app.modules.expenses.router import get_expense

        with pytest.raises(HTTPException) as exc_info:
            await get_expense(expense_id=expense_id, svc=mock_service, current_user=mock_user)
        
        assert exc_info.value.status_code == 404


class TestEditExpenseEndpoint:
    """PATCH /trips/{trip_id}/expenses/{expense_id} endpoint"""

    @pytest.fixture
    def mock_user(self):
        user = MagicMock(spec=User)
        user.id = uuid4()
        user.email = "test@example.com"
        user.role = UserRole.EMPLOYEE
        return user

    @pytest.fixture
    def mock_service(self):
        return AsyncMock(spec=ExpensesService)

    @pytest.fixture
    def mock_expense(self):
        expense = MagicMock(spec=Expense)
        expense.id = uuid4()
        expense.trip_id = uuid4()
        expense.type = "Tolls"
        expense.amount = 2500.0
        return expense

    @pytest.mark.asyncio
    async def test_edit_expense_success(self, mock_service, mock_expense, mock_user):

        expense_id = uuid4()
        request_body = {"type": "Tolls", "amount": 2500.0}
        mock_service.edit_expense.return_value = mock_expense

        from app.modules.expenses.router import edit_expense

        result = await edit_expense(
            expense_id=expense_id,
            body=EditExpenseDTO(**request_body),
            svc=mock_service,
            current_user=mock_user
        )

        assert result == mock_expense
        mock_service.edit_expense.assert_called_once_with(mock_user.id, expense_id, EditExpenseDTO(**request_body))

    @pytest.mark.asyncio
    async def test_edit_expense_partial_update(self, mock_service, mock_expense, mock_user):

        expense_id = uuid4()
        request_body = {"amount": 2500.0}
        mock_service.edit_expense.return_value = mock_expense

        from app.modules.expenses.router import edit_expense

        result = await edit_expense(
            expense_id=expense_id,
            body=EditExpenseDTO(**request_body),
            svc=mock_service,
            current_user=mock_user
        )

        assert result == mock_expense

    @pytest.mark.asyncio
    async def test_edit_expense_not_found(self, mock_service, mock_user):

        expense_id = uuid4()
        request_body = {"type": "Tolls"}
        mock_service.edit_expense.side_effect = ExpenseNotFoundError("Expense not found")

        from app.modules.expenses.router import edit_expense

        with pytest.raises(HTTPException) as exc_info:
            await edit_expense(
                expense_id=expense_id,
                body=EditExpenseDTO(**request_body),
                svc=mock_service,
                current_user=mock_user
            )
        
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_edit_expense_invalid_data(self, mock_service, mock_user):

        expense_id = uuid4()
        request_body = {"amount": -100.0}
        mock_service.edit_expense.side_effect = InvalidExpenseDataError("Amount must be positive")

        from app.modules.expenses.router import edit_expense

        with pytest.raises(HTTPException) as exc_info:
            await edit_expense(
                expense_id=expense_id,
                body=EditExpenseDTO(**request_body),
                svc=mock_service,
                current_user=mock_user
            )
        
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_edit_expense_duplicate_type(self, mock_service, mock_user):

        expense_id = uuid4()
        request_body = {"type": "Parking"}
        mock_service.edit_expense.side_effect = DuplicateExpenseError(
            "An expense with this type already exists"
        )

        from app.modules.expenses.router import edit_expense

        with pytest.raises(HTTPException) as exc_info:
            await edit_expense(
                expense_id=expense_id,
                body=EditExpenseDTO(**request_body),
                svc=mock_service,
                current_user=mock_user
            )
        
        assert exc_info.value.status_code == 409


class TestDeleteExpenseEndpoint:
    """DELETE /trips/{trip_id}/expenses/{expense_id} endpoint"""

    @pytest.fixture
    def mock_user(self):
        user = MagicMock(spec=User)
        user.id = uuid4()
        user.email = "test@example.com"
        user.role = UserRole.EMPLOYEE
        return user

    @pytest.fixture
    def mock_service(self):
        user = MagicMock(spec=User)
        user.id = uuid4()
        user.email = "test@example.com"
        user.role = UserRole.EMPLOYEE
        return user

    @pytest.fixture
    def mock_service(self):
        return AsyncMock(spec=ExpensesService)

    @pytest.mark.asyncio
    async def test_delete_expense_success(self, mock_service, mock_user):

        expense_id = uuid4()
        mock_service.delete_expense.return_value = None

        from app.modules.expenses.router import delete_expense

        result = await delete_expense(expense_id=expense_id, svc=mock_service, current_user=mock_user)

        assert result.status_code == status.HTTP_204_NO_CONTENT
        mock_service.delete_expense.assert_called_once_with(mock_user.id, expense_id)

    @pytest.mark.asyncio
    async def test_delete_expense_not_found(self, mock_service, mock_user):

        expense_id = uuid4()
        mock_service.delete_expense.side_effect = ExpenseNotFoundError("Expense not found")

        from app.modules.expenses.router import delete_expense

        with pytest.raises(HTTPException) as exc_info:
            await delete_expense(expense_id=expense_id, svc=mock_service, current_user=mock_user)
        
        assert exc_info.value.status_code == 404


class TestGetExpensesServiceDependency:

    def test_get_expenses_service_returns_service(self):
        mock_db = MagicMock()

        service = get_expenses_service(db=mock_db)

        assert isinstance(service, ExpensesService)
        assert service.expense_repo is not None
        assert service.trip_repo is not None
