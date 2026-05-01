import pytest
from unittest.mock import MagicMock

from app.modules.expenses.repository import ExpenseRepo
from app.modules.expenses.models import Expense


class TestExpenseRepoSave:
    @pytest.fixture
    def repo(self, mock_db_session):
        return ExpenseRepo(mock_db_session)

    @pytest.fixture
    def mock_expense(self, sample_expense_id, sample_trip_id):
        expense = MagicMock(spec=Expense)
        expense.id = sample_expense_id
        expense.trip_id = sample_trip_id
        expense.type = "Parking"
        expense.amount = 15.50
        return expense

    @pytest.mark.asyncio
    async def test_save_expense(self, repo, mock_db_session, mock_expense):

        result = await repo.save(mock_expense)

        mock_db_session.add.assert_called_once_with(mock_expense)
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(mock_expense)
        assert result == mock_expense


class TestExpenseRepoGetExpense:

    @pytest.fixture
    def repo(self, mock_db_session):
        return ExpenseRepo(mock_db_session)

    @pytest.fixture
    def mock_expense(self, sample_expense_id, sample_trip_id):
        expense = MagicMock(spec=Expense)
        expense.id = sample_expense_id
        expense.trip_id = sample_trip_id
        expense.type = "Parking"
        expense.amount = 12.25
        return expense

    @pytest.mark.asyncio
    async def test_get_expense_found(self, repo, mock_db_session, mock_expense, sample_expense_id):

        mock_db_session.scalar.return_value = mock_expense

        result = await repo.get_expense(sample_expense_id)

        assert result == mock_expense
        mock_db_session.scalar.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_expense_not_found(self, repo, mock_db_session, sample_expense_id):
        
        mock_db_session.scalar.return_value = None

        result = await repo.get_expense(sample_expense_id)

        assert result is None
        mock_db_session.scalar.assert_called_once()


class TestExpenseRepoGetExpensesByTripId:

    @pytest.fixture
    def repo(self, mock_db_session):
        return ExpenseRepo(mock_db_session)

    @pytest.fixture
    def mock_expenses(self, sample_expense_id):
        expenses = []
        for i in range(3):
            expense = MagicMock(spec=Expense)
            expense.id = sample_expense_id
            expense.type = f"Type{i}"
            expense.amount = 10.50 * (i + 1)
            expenses.append(expense)
        return expenses

    @pytest.mark.asyncio
    async def test_get_expenses_by_trip_id_found(self, repo, mock_db_session, mock_expenses, sample_trip_id):

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_expenses
        mock_db_session.execute.return_value = mock_result

        result = await repo.get_expenses_by_trip_id(sample_trip_id)

        assert result == mock_expenses
        assert len(result) == 3
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_expenses_by_trip_id_empty(self, repo, mock_db_session, sample_trip_id):

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result

        result = await repo.get_expenses_by_trip_id(sample_trip_id)

        assert result == []
        mock_db_session.execute.assert_called_once()


class TestExpenseRepoGetByTripAndType:

    @pytest.fixture
    def repo(self, mock_db_session):
        return ExpenseRepo(mock_db_session)

    @pytest.fixture
    def mock_expense(self, sample_expense_id, sample_trip_id):
        expense = MagicMock(spec=Expense)
        expense.id = sample_expense_id
        expense.trip_id = sample_trip_id
        expense.type = "Parking"
        expense.amount = 8.75
        return expense

    @pytest.mark.asyncio
    async def test_get_by_trip_and_type_found(self, repo, mock_db_session, mock_expense, sample_trip_id):

        expense_type = "Parking"
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_expense
        mock_db_session.execute.return_value = mock_result

        result = await repo.get_by_trip_and_type(sample_trip_id, expense_type)

        assert result == mock_expense
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_trip_and_type_not_found(self, repo, mock_db_session, sample_trip_id):

        expense_type = "Tolls"
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        result = await repo.get_by_trip_and_type(sample_trip_id, expense_type)

        assert result is None
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_trip_and_type_case_insensitive(self, repo, mock_db_session, mock_expense, sample_trip_id):

        expense_type = "parking"
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_expense
        mock_db_session.execute.return_value = mock_result

        result = await repo.get_by_trip_and_type(sample_trip_id, expense_type)

        assert result == mock_expense


class TestExpenseRepoDeleteExpense:

    @pytest.fixture
    def repo(self, mock_db_session):
        return ExpenseRepo(mock_db_session)

    @pytest.fixture
    def mock_expense(self, sample_expense_id, sample_trip_id):
        expense = MagicMock(spec=Expense)
        expense.id = sample_expense_id
        expense.trip_id = sample_trip_id
        expense.type = "Parking"
        expense.amount = 6.50
        return expense

    @pytest.mark.asyncio
    async def test_delete_expense_success(self, repo, mock_db_session, mock_expense):

        await repo.delete_expense(mock_expense)

        mock_db_session.delete.assert_called_once_with(mock_expense)
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_expense_returns_none(self, repo, mock_db_session, mock_expense):
        result = await repo.delete_expense(mock_expense)

        assert result is None


class TestExpenseRepoSumByTrip:

    @pytest.fixture
    def repo(self, mock_db_session):
        return ExpenseRepo(mock_db_session)

    @pytest.mark.asyncio
    async def test_sum_by_trip_with_expenses(self, repo, mock_db_session, sample_trip_id):

        expected_sum = 45.75
        mock_result = MagicMock()
        mock_result.scalar.return_value = expected_sum
        mock_db_session.execute.return_value = mock_result

        result = await repo.sum_by_trip(sample_trip_id)

        assert result == expected_sum
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_sum_by_trip_no_expenses(self, repo, mock_db_session, sample_trip_id):

        mock_result = MagicMock()
        mock_result.scalar.return_value = None
        mock_db_session.execute.return_value = mock_result

        result = await repo.sum_by_trip(sample_trip_id)

        assert result == 0.0
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_sum_by_trip_single_expense(self, repo, mock_db_session, sample_trip_id):

        expected_sum = 15.00
        mock_result = MagicMock()
        mock_result.scalar.return_value = expected_sum
        mock_db_session.execute.return_value = mock_result

        result = await repo.sum_by_trip(sample_trip_id)

        assert result == expected_sum