import pytest
from uuid import uuid4
from datetime import datetime, timezone
from pydantic import ValidationError

from app.modules.expenses.schemas import CreateExpenseDTO, EditExpenseDTO, ExpenseResponseDTO


class TestCreateExpenseDTO:

    def test_create_expense_dto_valid(self):
        data = {"type": "Parking", "amount": 15.50}
        
        dto = CreateExpenseDTO(**data)
        
        assert dto.type == "Parking"
        assert dto.amount == 15.50

    def test_create_expense_dto_missing_required_fields(self):
        with pytest.raises(ValidationError):
            CreateExpenseDTO(type="Parking")
        
        with pytest.raises(ValidationError):
            CreateExpenseDTO(amount=15.50)


class TestEditExpenseDTO:

    def test_edit_expense_dto_all_fields(self):
        dto = EditExpenseDTO(type="Tolls", amount=25.00)
        
        assert dto.type == "Tolls"
        assert dto.amount == 25.00

    def test_edit_expense_dto_partial_fields(self):
        dto1 = EditExpenseDTO(type="Tolls")
        assert dto1.type == "Tolls"
        assert dto1.amount is None
        
        dto2 = EditExpenseDTO(amount=25.00)
        assert dto2.type is None
        assert dto2.amount == 25.00

    def test_edit_expense_dto_empty(self):
        dto = EditExpenseDTO()
        
        assert dto.type is None
        assert dto.amount is None


class TestExpenseResponseDTO:

    def test_expense_response_dto_valid(self):
        expense_id = uuid4()
        trip_id = uuid4()
        created_at = datetime.now(timezone.utc)
        
        dto = ExpenseResponseDTO(
            id=expense_id,
            trip_id=trip_id,
            type="Parking",
            amount=15.50,
            created_at=created_at
        )
        
        assert dto.id == expense_id
        assert dto.trip_id == trip_id
        assert dto.type == "Parking"
        assert dto.amount == 15.50
        assert dto.created_at == created_at

    def test_expense_response_dto_from_orm(self):
        from unittest.mock import MagicMock
        from app.modules.expenses.models import Expense
        
        expense_id = uuid4()
        trip_id = uuid4()
        created_at = datetime.now(timezone.utc)
        
        mock_expense = MagicMock(spec=Expense)
        mock_expense.id = expense_id
        mock_expense.trip_id = trip_id
        mock_expense.type = "Parking"
        mock_expense.amount = 15.50
        mock_expense.created_at = created_at
        
        dto = ExpenseResponseDTO.model_validate(mock_expense)
        
        assert dto.id == expense_id
        assert dto.trip_id == trip_id
        assert dto.type == "Parking"
        assert dto.amount == 15.50
        assert dto.created_at == created_at

    def test_expense_response_dto_missing_required_fields(self):
        with pytest.raises(ValidationError):
            ExpenseResponseDTO(
                trip_id=uuid4(),
                type="Parking",
                amount=15.50,
                created_at=datetime.now(timezone.utc)
            )
