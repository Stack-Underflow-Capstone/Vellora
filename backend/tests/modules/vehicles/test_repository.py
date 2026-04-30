import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.modules.vehicles.repository import VehicleRepository
from app.modules.vehicles.models import Vehicle


class TestVehicleRepository:

    @pytest.fixture
    def mock_session(self):
        return AsyncMock()

    @pytest.fixture
    def repository(self, mock_session):
        return VehicleRepository(mock_session)

    @pytest.fixture
    def mock_vehicle(self):
        vehicle = MagicMock(spec=Vehicle)
        vehicle.id = uuid4()
        vehicle.user_id = uuid4()
        vehicle.name = "Personal Car"
        vehicle.license_plate = "ABC123"
        return vehicle

    @pytest.mark.asyncio
    async def test_save_vehicle(self, repository, mock_session, mock_vehicle):
        result = await repository.save(mock_vehicle)
        
        mock_session.add.assert_called_once_with(mock_vehicle)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(mock_vehicle)
        assert result == mock_vehicle

    @pytest.mark.asyncio
    async def test_delete_vehicle(self, repository, mock_vehicle, mock_session):
        await repository.delete(mock_vehicle)
        
        mock_session.delete.assert_called_once_with(mock_vehicle)
        mock_session.commit.assert_called_once()


class TestSaveVehicle:
    @pytest.mark.asyncio
    async def test_save_vehicle_success(self, mock_db_session):
        # Arrange
        vehicle = Vehicle(
            id=uuid4(),
            user_id=uuid4(),
            name="Test Car",
            license_plate="ABC123",
            model="Camry",
            year=2020,
            color="Blue",
            is_active=True
        )
        mock_db_session.add = AsyncMock()
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()
        
        # Act
        from app.modules.vehicles.repository import VehicleRepository
        vehicle_repo = VehicleRepository(mock_db_session)
        result = await vehicle_repo.save(vehicle)
        
        # Assert
        mock_db_session.add.assert_called_once_with(vehicle)
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(vehicle)
        assert result == vehicle

    @pytest.mark.asyncio
    async def test_save_vehicle_commit_error(self, mock_db_session):
        # Arrange
        vehicle = Vehicle(id=uuid4(), user_id=uuid4(), name="Test Car", license_plate="ABC123", model="Camry")
        mock_db_session.add = AsyncMock()
        mock_db_session.commit = AsyncMock(side_effect=Exception("Database error"))
        
        # Act & Assert
        from app.modules.vehicles.repository import VehicleRepository
        vehicle_repo = VehicleRepository(mock_db_session)
        with pytest.raises(Exception, match="Database error"):
            await vehicle_repo.save(vehicle)


class TestUpdateVehicle:
    @pytest.mark.asyncio
    async def test_update_vehicle_success(self, mock_db_session):
        # Arrange
        vehicle = Vehicle(
            id=uuid4(),
            user_id=uuid4(),
            name="Updated Car",
            license_plate="XYZ789",
            model="Civic",
            year=2021,
            color="Red",
            is_active=True
        )
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()
        
        # Act
        from app.modules.vehicles.repository import VehicleRepository
        vehicle_repo = VehicleRepository(mock_db_session)
        result = await vehicle_repo.update(vehicle)
        
        # Assert
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(vehicle)
        assert result == vehicle

    @pytest.mark.asyncio
    async def test_update_vehicle_commit_error(self, mock_db_session):
        # Arrange
        vehicle = Vehicle(id=uuid4(), user_id=uuid4(), name="Updated Car", license_plate="ABC123", model="Camry")
        mock_db_session.commit = AsyncMock(side_effect=Exception("Commit error"))
        
        # Act & Assert
        from app.modules.vehicles.repository import VehicleRepository
        vehicle_repo = VehicleRepository(mock_db_session)
        with pytest.raises(Exception, match="Commit error"):
            await vehicle_repo.update(vehicle)


class TestGetVehiclesByUser:
    @pytest.mark.asyncio
    async def test_get_by_user_success(self, mock_db_session):
        # Arrange
        user_id = uuid4()
        mock_vehicles = [
            Vehicle(id=uuid4(), user_id=user_id, name="Car 1", license_plate="ABC123", model="Camry"),
            Vehicle(id=uuid4(), user_id=user_id, name="Car 2", license_plate="XYZ789", model="Civic")
        ]
        
        mock_result = AsyncMock()
        mock_result.scalars = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_vehicles
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        # Act
        from app.modules.vehicles.repository import VehicleRepository
        vehicle_repo = VehicleRepository(mock_db_session)
        result = await vehicle_repo.get_by_user(user_id)
        
        # Assert
        mock_db_session.execute.assert_called_once()
        assert result == mock_vehicles

    @pytest.mark.asyncio
    async def test_get_by_user_empty_result(self, mock_db_session):
        # Arrange
        user_id = uuid4()
        mock_result = AsyncMock()
        mock_result.scalars = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        # Act
        from app.modules.vehicles.repository import VehicleRepository
        vehicle_repo = VehicleRepository(mock_db_session)
        result = await vehicle_repo.get_by_user(user_id)
        
        # Assert
        mock_db_session.execute.assert_called_once()
        assert result == []

    @pytest.mark.asyncio
    async def test_get_by_user_with_inactive(self, mock_db_session):
        # Arrange
        user_id = uuid4()
        mock_vehicles = [
            Vehicle(id=uuid4(), user_id=user_id, name="Active Car", license_plate="ABC123", model="Camry"),
            Vehicle(id=uuid4(), user_id=user_id, name="Inactive Car", license_plate="XYZ789", model="Civic")
        ]
        
        mock_result = AsyncMock()
        mock_result.scalars = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_vehicles
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        # Act
        from app.modules.vehicles.repository import VehicleRepository
        vehicle_repo = VehicleRepository(mock_db_session)
        result = await vehicle_repo.get_by_user(user_id, include_inactive=True)
        
        # Assert
        mock_db_session.execute.assert_called_once()
        assert result == mock_vehicles


class TestGetVehicleById:
    @pytest.mark.asyncio
    async def test_get_by_id_found(self, mock_db_session):
        # Arrange
        vehicle_id = uuid4()
        user_id = uuid4()
        mock_vehicle = Vehicle(id=vehicle_id, user_id=user_id, name="Test Car", license_plate="ABC123", model="Camry")
        
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_vehicle)
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        # Act
        from app.modules.vehicles.repository import VehicleRepository
        vehicle_repo = VehicleRepository(mock_db_session)
        result = await vehicle_repo.get_by_id(vehicle_id, user_id)
        
        # Assert
        mock_db_session.execute.assert_called_once()
        assert result == mock_vehicle

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, mock_db_session):
        # Arrange
        vehicle_id = uuid4()
        user_id = uuid4()
        
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        # Act
        from app.modules.vehicles.repository import VehicleRepository
        vehicle_repo = VehicleRepository(mock_db_session)
        result = await vehicle_repo.get_by_id(vehicle_id, user_id)
        
        # Assert
        mock_db_session.execute.assert_called_once()
        assert result is None