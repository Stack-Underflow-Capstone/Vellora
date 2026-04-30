import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from fastapi import status, HTTPException

from app.modules.vehicles.service import VehicleService
from app.modules.vehicles.schemas import CreateVehicleDTO, EditVehicleDTO, VehicleResponse
from app.modules.users.models import User, UserRole


class TestCreateVehicleEndpoint:
    """POST /vehicles/ endpoint"""

    @pytest.fixture
    def mock_user(self):
        user = MagicMock(spec=User)
        user.id = uuid4()
        user.email = "test@example.com"
        user.role = UserRole.EMPLOYEE
        return user

    @pytest.fixture
    def mock_service(self):
        return AsyncMock(spec=VehicleService)

    @pytest.fixture
    def mock_vehicle(self):
        from app.modules.vehicles.models import Vehicle
        vehicle = MagicMock(spec=Vehicle)
        vehicle.id = uuid4()
        vehicle.name = "Test Vehicle"
        vehicle.license_plate = "ABC123"
        vehicle.model = "Toyota Camry" 
        vehicle.year = 2020
        vehicle.color = "Blue"
        vehicle.is_active = True
        return vehicle

    @pytest.mark.asyncio
    async def test_create_vehicle_success(self, mock_service, mock_vehicle, mock_user):
        from app.modules.vehicles.router import create_vehicle
        
        request_body = CreateVehicleDTO(
            name="My Car",
            license_plate="ABC123",
            model="Toyota Camry",
            year=2020,
            color="Blue"
        )
        mock_service.create_vehicle.return_value = mock_vehicle

        with patch('app.modules.vehicles.router.VehicleResponse.model_validate') as mock_validate:
            mock_validate.return_value = MagicMock()
            result = await create_vehicle(request_body, mock_service, mock_user)

        mock_service.create_vehicle.assert_called_once_with(mock_user.id, request_body)
        mock_validate.assert_called_once_with(mock_vehicle)

    @pytest.mark.asyncio
    async def test_create_vehicle_duplicate_name(self, mock_service, mock_user):
        from app.modules.vehicles.router import create_vehicle
        from app.modules.vehicles.exceptions import DuplicateVehicleError
        
        request_body = CreateVehicleDTO(
            name="Existing Car",
            license_plate="DEF456",
            model="Honda Civic",
            year=2021,
            color="Red"
        )
        mock_service.create_vehicle.side_effect = DuplicateVehicleError("Vehicle with this name already exists")

        with pytest.raises(HTTPException) as exc_info:
            await create_vehicle(request_body, mock_service, mock_user)

        assert exc_info.value.status_code == status.HTTP_409_CONFLICT


class TestGetVehiclesEndpoint:
    """GET /vehicles/ endpoint"""

    @pytest.fixture
    def mock_user(self):
        user = MagicMock(spec=User)
        user.id = uuid4()
        user.email = "test@example.com"
        user.role = UserRole.EMPLOYEE
        return user

    @pytest.fixture
    def mock_service(self):
        return AsyncMock(spec=VehicleService)

    @pytest.mark.asyncio
    async def test_get_vehicles_success(self, mock_service, mock_user):
        from app.modules.vehicles.router import get_user_vehicles
        
        mock_vehicles = [MagicMock(), MagicMock()]
        mock_service.get_user_vehicles.return_value = mock_vehicles

        with patch('app.modules.vehicles.router.VehicleResponse.model_validate') as mock_validate:
            mock_validate.side_effect = [MagicMock(), MagicMock()]
            result = await get_user_vehicles(False, mock_service, mock_user)

        mock_service.get_user_vehicles.assert_called_once_with(mock_user.id, False)
        assert mock_validate.call_count == 2

    @pytest.mark.asyncio
    async def test_get_vehicles_with_inactive(self, mock_service, mock_user):
        from app.modules.vehicles.router import get_user_vehicles
        
        mock_vehicles = [MagicMock(), MagicMock(), MagicMock()]
        mock_service.get_user_vehicles.return_value = mock_vehicles

        with patch('app.modules.vehicles.router.VehicleResponse.model_validate') as mock_validate:
            mock_validate.side_effect = [MagicMock(), MagicMock(), MagicMock()]
            result = await get_user_vehicles(True, mock_service, mock_user)

        mock_service.get_user_vehicles.assert_called_once_with(mock_user.id, True)
        assert mock_validate.call_count == 3


class TestGetVehicleEndpoint:
    """GET /vehicles/{vehicle_id} endpoint"""

    @pytest.fixture
    def mock_user(self):
        user = MagicMock(spec=User)
        user.id = uuid4()
        user.email = "test@example.com"
        user.role = UserRole.EMPLOYEE
        return user

    @pytest.fixture
    def mock_service(self):
        return AsyncMock(spec=VehicleService)

    @pytest.fixture
    def mock_vehicle(self):
        from app.modules.vehicles.models import Vehicle
        vehicle = MagicMock(spec=Vehicle)
        vehicle.id = uuid4()
        vehicle.name = "Test Vehicle"
        vehicle.license_plate = "ABC123"
        vehicle.model = "Toyota Camry"
        vehicle.year = 2020
        vehicle.color = "Blue"
        vehicle.is_active = True
        return vehicle

    @pytest.fixture
    def mock_vehicle(self):
        from app.modules.vehicles.models import Vehicle
        vehicle = MagicMock(spec=Vehicle)
        vehicle.id = uuid4()
        vehicle.name = "Test Vehicle"
        vehicle.license_plate = "ABC123"
        vehicle.model = "Toyota Camry"
        vehicle.year = 2020
        vehicle.color = "Blue"
        vehicle.is_active = True
        return vehicle

    @pytest.mark.asyncio
    async def test_get_vehicle_success(self, mock_service, mock_vehicle, mock_user):
        from app.modules.vehicles.router import get_vehicle
        
        vehicle_id = uuid4()
        mock_service.get_vehicle.return_value = mock_vehicle

        with patch('app.modules.vehicles.router.VehicleResponse.model_validate') as mock_validate:
            mock_validate.return_value = MagicMock()
            result = await get_vehicle(vehicle_id, mock_service, mock_user)

        mock_service.get_vehicle.assert_called_once_with(mock_user.id, vehicle_id)
        mock_validate.assert_called_once_with(mock_vehicle)

    @pytest.mark.asyncio
    async def test_get_vehicle_not_found(self, mock_service, mock_user):
        from app.modules.vehicles.router import get_vehicle
        from app.modules.vehicles.exceptions import VehicleNotFoundError
        
        vehicle_id = uuid4()
        mock_service.get_vehicle.side_effect = VehicleNotFoundError("Vehicle not found")

        with pytest.raises(HTTPException) as exc_info:
            await get_vehicle(vehicle_id, mock_service, mock_user)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateVehicleEndpoint:
    """PATCH /vehicles/{vehicle_id} endpoint"""

    @pytest.fixture
    def mock_user(self):
        user = MagicMock(spec=User)
        user.id = uuid4()
        user.email = "test@example.com"
        user.role = UserRole.EMPLOYEE
        return user

    @pytest.fixture
    def mock_service(self):
        return AsyncMock(spec=VehicleService)

    @pytest.fixture
    def mock_vehicle(self):
        from app.modules.vehicles.models import Vehicle
        vehicle = MagicMock(spec=Vehicle)
        vehicle.id = uuid4()
        vehicle.name = "Test Vehicle"
        vehicle.license_plate = "ABC123"
        vehicle.model = "Toyota Camry"
        vehicle.year = 2020
        vehicle.color = "Blue"
        vehicle.is_active = True
        return vehicle

    @pytest.fixture
    def mock_vehicle(self):
        from app.modules.vehicles.models import Vehicle
        vehicle = MagicMock(spec=Vehicle)
        vehicle.id = uuid4()
        vehicle.name = "Test Vehicle"
        vehicle.license_plate = "ABC123"
        vehicle.model = "Toyota Camry"
        vehicle.year = 2020
        vehicle.color = "Blue"
        vehicle.is_active = True
        return vehicle

    @pytest.mark.asyncio
    async def test_update_vehicle_success(self, mock_service, mock_vehicle, mock_user):
        from app.modules.vehicles.router import update_vehicle
        
        vehicle_id = uuid4()
        update_data = EditVehicleDTO(
            name="Updated Car",
            color="Red"
        )
        mock_service.update_vehicle.return_value = mock_vehicle

        with patch('app.modules.vehicles.router.VehicleResponse.model_validate') as mock_validate:
            mock_validate.return_value = MagicMock()
            result = await update_vehicle(vehicle_id, update_data, mock_service, mock_user)

        mock_service.update_vehicle.assert_called_once_with(mock_user.id, vehicle_id, update_data)
        mock_validate.assert_called_once_with(mock_vehicle)

    @pytest.mark.asyncio
    async def test_update_vehicle_not_found(self, mock_service, mock_user):
        from app.modules.vehicles.router import update_vehicle
        from app.modules.vehicles.exceptions import VehicleNotFoundError
        
        vehicle_id = uuid4()
        update_data = EditVehicleDTO(name="Non-existent Car")
        mock_service.update_vehicle.side_effect = VehicleNotFoundError("Vehicle not found")

        with pytest.raises(HTTPException) as exc_info:
            await update_vehicle(vehicle_id, update_data, mock_service, mock_user)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_update_vehicle_duplicate_name(self, mock_service, mock_user):
        from app.modules.vehicles.router import update_vehicle
        from app.modules.vehicles.exceptions import DuplicateVehicleError
        
        vehicle_id = uuid4()
        update_data = EditVehicleDTO(name="Existing Vehicle Name")
        mock_service.update_vehicle.side_effect = DuplicateVehicleError("Vehicle with this name already exists")

        with pytest.raises(HTTPException) as exc_info:
            await update_vehicle(vehicle_id, update_data, mock_service, mock_user)

        assert exc_info.value.status_code == status.HTTP_409_CONFLICT


class TestDeleteVehicleEndpoint:
    """DELETE /vehicles/{vehicle_id} endpoint"""

    @pytest.fixture
    def mock_user(self):
        user = MagicMock(spec=User)
        user.id = uuid4()
        user.email = "test@example.com"
        user.role = UserRole.EMPLOYEE
        return user

    @pytest.fixture
    def mock_service(self):
        return AsyncMock(spec=VehicleService)

    @pytest.mark.asyncio
    async def test_delete_vehicle_success(self, mock_service, mock_user):
        from app.modules.vehicles.router import delete_vehicle
        
        vehicle_id = uuid4()
        mock_service.delete_vehicle.return_value = None

        result = await delete_vehicle(vehicle_id, mock_service, mock_user)

        mock_service.delete_vehicle.assert_called_once_with(mock_user.id, vehicle_id)
        assert result.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.asyncio
    async def test_delete_vehicle_not_found(self, mock_service, mock_user):
        from app.modules.vehicles.router import delete_vehicle
        from app.modules.vehicles.exceptions import VehicleNotFoundError
        
        vehicle_id = uuid4()
        mock_service.delete_vehicle.side_effect = VehicleNotFoundError("Vehicle not found")

        with pytest.raises(HTTPException) as exc_info:
            await delete_vehicle(vehicle_id, mock_service, mock_user)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


class TestGetVehicleServiceDependency:
    """Test the get_vehicle_service dependency function"""

    @pytest.mark.asyncio
    async def test_get_service_returns_service(self):
        from app.modules.vehicles.router import get_vehicle_service
        mock_db = AsyncMock()
        service = get_vehicle_service(mock_db)
        assert isinstance(service, VehicleService)