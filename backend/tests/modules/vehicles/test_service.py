import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.modules.vehicles.service import VehicleService
from app.modules.vehicles.repository import VehicleRepository
from app.modules.vehicles.schemas import CreateVehicleDTO, EditVehicleDTO
from app.modules.vehicles.models import Vehicle
from app.modules.vehicles.exceptions import (
    VehicleNotFoundError,
    DuplicateVehicleError,
    InvalidVehicleDataError,
    VehiclePersistenceError
)


@pytest.fixture
def user_id():
    return uuid4()


@pytest.fixture
def vehicle_repo():
    return AsyncMock(spec=VehicleRepository)


@pytest.fixture 
def vehicle_service(vehicle_repo):
    return VehicleService(vehicle_repo)


@pytest.fixture
def mock_vehicle():
    return MagicMock(spec=Vehicle)


@pytest.fixture
def create_vehicle_dto():
    return CreateVehicleDTO(
        name="Test Car",
        license_plate="ABC123",
        model="Toyota Camry", 
        year=2020,
        color="Blue"
    )


class TestVehicleServiceCreateVehicle:

    @pytest.mark.asyncio
    async def test_create_vehicle_success(self, vehicle_service, vehicle_repo, user_id, create_vehicle_dto, mock_vehicle):
        vehicle_repo.get_by_name.return_value = None
        vehicle_repo.get_by_license_plate.return_value = None
        vehicle_repo.save.return_value = mock_vehicle
        
        with patch('app.modules.vehicles.service.Vehicle', return_value=mock_vehicle):
            result = await vehicle_service.create_vehicle(user_id, create_vehicle_dto)
        
        assert result == mock_vehicle
        vehicle_repo.save.assert_called_once_with(mock_vehicle)
        vehicle_repo.get_by_name.assert_called_once_with(user_id, create_vehicle_dto.name.strip())
        vehicle_repo.get_by_license_plate.assert_called_once_with(user_id, create_vehicle_dto.license_plate.upper())

    @pytest.mark.asyncio
    async def test_create_vehicle_duplicate_name(self, vehicle_service, vehicle_repo, user_id, create_vehicle_dto, mock_vehicle):
        vehicle_repo.get_by_name.return_value = mock_vehicle
        
        with pytest.raises(DuplicateVehicleError) as exc_info:
            await vehicle_service.create_vehicle(user_id, create_vehicle_dto)
        
        assert "A vehicle with this name already exists" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_vehicle_duplicate_license_plate(self, vehicle_service, vehicle_repo, user_id, create_vehicle_dto, mock_vehicle):
        vehicle_repo.get_by_name.return_value = None
        vehicle_repo.get_by_license_plate.return_value = mock_vehicle
        
        with pytest.raises(DuplicateVehicleError) as exc_info:
            await vehicle_service.create_vehicle(user_id, create_vehicle_dto)
        
        assert "A vehicle with this license plate already exists" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_vehicle_empty_name(self, vehicle_service, user_id):
        dto = CreateVehicleDTO(name="", license_plate="ABC123", model="Toyota", year=2020, color="Blue")
        
        with pytest.raises(InvalidVehicleDataError) as exc_info:
            await vehicle_service.create_vehicle(user_id, dto)
        
        assert "Vehicle name is required" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_vehicle_empty_license_plate(self, vehicle_service, user_id):
        dto = CreateVehicleDTO(name="My Car", license_plate="", model="Toyota", year=2020, color="Blue")
        
        with pytest.raises(InvalidVehicleDataError) as exc_info:
            await vehicle_service.create_vehicle(user_id, dto)
        
        assert "License plate is required" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_vehicle_empty_model(self, vehicle_service, user_id):
        dto = CreateVehicleDTO(name="My Car", license_plate="ABC123", model="", year=2020, color="Blue")
        
        with pytest.raises(InvalidVehicleDataError) as exc_info:
            await vehicle_service.create_vehicle(user_id, dto)
        
        assert "Vehicle model is required" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_vehicle_uppercase_license_plate(self, vehicle_service, vehicle_repo, user_id, mock_vehicle):
        dto = CreateVehicleDTO(name="My Car", license_plate="abc123", model="Toyota", year=2020, color="Blue")
        vehicle_repo.get_by_name.return_value = None
        vehicle_repo.get_by_license_plate.return_value = None
        vehicle_repo.save.return_value = mock_vehicle
        
        with patch('app.modules.vehicles.service.Vehicle', return_value=mock_vehicle) as mock_class:
            await vehicle_service.create_vehicle(user_id, dto)
        
        # Verify license plate was converted to uppercase
        mock_class.assert_called_once()
        call_args = mock_class.call_args[1]
        assert call_args['license_plate'] == 'ABC123'

    @pytest.mark.asyncio
    async def test_create_vehicle_invalid_year_too_low(self, vehicle_service, user_id):
        dto = CreateVehicleDTO(name="Test Car", license_plate="ABC123", model="Toyota", year=1800, color="Blue")
        
        with pytest.raises(InvalidVehicleDataError) as exc_info:
            await vehicle_service.create_vehicle(user_id, dto)
        assert "year must be between 1900 and 2100" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_vehicle_invalid_year_too_high(self, vehicle_service, user_id):
        dto = CreateVehicleDTO(name="Test Car", license_plate="ABC123", model="Toyota", year=2200, color="Blue")
        
        with pytest.raises(InvalidVehicleDataError) as exc_info:
            await vehicle_service.create_vehicle(user_id, dto)
        assert "year must be between 1900 and 2100" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_vehicle_year_zero_invalid(self, vehicle_service, user_id):
        dto = CreateVehicleDTO(name="Test Car", license_plate="ABC123", model="Toyota", year=0, color="Blue")
        
        with pytest.raises(InvalidVehicleDataError) as exc_info:
            await vehicle_service.create_vehicle(user_id, dto)
        assert "year must be between 1900 and 2100" in str(exc_info.value)


class TestVehicleServiceGetVehicle:

    @pytest.fixture
    def user_id(self):
        return uuid4()

    @pytest.fixture
    def vehicle_id(self):
        return uuid4()

    @pytest.fixture
    def vehicle_repo(self):
        return AsyncMock(spec=VehicleRepository)

    @pytest.fixture
    def service(self, vehicle_repo):
        return VehicleService(vehicle_repo)

    @pytest.fixture
    def mock_vehicle(self):
        return MagicMock(spec=Vehicle)

    @pytest.mark.asyncio
    async def test_get_vehicle_success(self, service, vehicle_repo, user_id, vehicle_id, mock_vehicle):
        vehicle_repo.get_by_id.return_value = mock_vehicle
        
        result = await service.get_vehicle(user_id, vehicle_id)
        
        assert result == mock_vehicle
        vehicle_repo.get_by_id.assert_called_once_with(vehicle_id, user_id)

    @pytest.mark.asyncio
    async def test_get_vehicle_not_found(self, service, vehicle_repo, user_id, vehicle_id):
        vehicle_repo.get_by_id.return_value = None
        
        with pytest.raises(VehicleNotFoundError) as exc_info:
            await service.get_vehicle(user_id, vehicle_id)
        
        assert "Vehicle not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_user_vehicles(self, service, vehicle_repo, user_id):
        mock_vehicles = [MagicMock(spec=Vehicle), MagicMock(spec=Vehicle)]
        vehicle_repo.get_by_user.return_value = mock_vehicles
        
        result = await service.get_user_vehicles(user_id)
        
        assert result == mock_vehicles
        vehicle_repo.get_by_user.assert_called_once_with(user_id, False)

    @pytest.mark.asyncio
    async def test_get_user_vehicles_include_inactive(self, service, vehicle_repo, user_id):
        mock_vehicles = [MagicMock(spec=Vehicle), MagicMock(spec=Vehicle)]
        vehicle_repo.get_by_user.return_value = mock_vehicles
        
        result = await service.get_user_vehicles(user_id, include_inactive=True)
        
        assert result == mock_vehicles
        vehicle_repo.get_by_user.assert_called_once_with(user_id, True)


class TestVehicleServiceUpdateVehicle:

    @pytest.fixture
    def user_id(self):
        return uuid4()

    @pytest.fixture
    def vehicle_id(self):
        return uuid4()

    @pytest.fixture
    def vehicle_repo(self):
        return AsyncMock(spec=VehicleRepository)

    @pytest.fixture
    def service(self, vehicle_repo):
        return VehicleService(vehicle_repo)

    @pytest.fixture
    def mock_vehicle(self):
        vehicle = MagicMock(spec=Vehicle)
        vehicle.id = uuid4()
        vehicle.name = "Old Car"
        vehicle.license_plate = "OLD123"
        vehicle.model = "Old Model"
        vehicle.year = 2019
        vehicle.color = "Red"
        vehicle.is_active = True
        return vehicle

    @pytest.mark.asyncio
    async def test_update_vehicle_name_success(self, service, vehicle_repo, user_id, vehicle_id, mock_vehicle):
        dto = EditVehicleDTO(name="New Car Name")
        vehicle_repo.get_by_id.return_value = mock_vehicle
        vehicle_repo.get_by_name.return_value = None
        vehicle_repo.update.return_value = mock_vehicle
        
        result = await service.update_vehicle(user_id, vehicle_id, dto)
        
        assert result == mock_vehicle
        assert mock_vehicle.name == "New Car Name"
        vehicle_repo.update.assert_called_once_with(mock_vehicle)

    @pytest.mark.asyncio
    async def test_update_vehicle_duplicate_name(self, service, vehicle_repo, user_id, vehicle_id, mock_vehicle):
        dto = EditVehicleDTO(name="Existing Car")
        existing_vehicle = MagicMock(spec=Vehicle)
        existing_vehicle.id = uuid4()
        
        vehicle_repo.get_by_id.return_value = mock_vehicle
        vehicle_repo.get_by_name.return_value = existing_vehicle
        
        with pytest.raises(DuplicateVehicleError):
            await service.update_vehicle(user_id, vehicle_id, dto)

    @pytest.mark.asyncio
    async def test_update_vehicle_empty_name(self, service, vehicle_repo, user_id, vehicle_id, mock_vehicle):
        dto = EditVehicleDTO(name="   ")
        vehicle_repo.get_by_id.return_value = mock_vehicle
        
        with pytest.raises(InvalidVehicleDataError) as exc_info:
            await service.update_vehicle(user_id, vehicle_id, dto)
        
        assert "Vehicle name cannot be empty" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_vehicle_license_plate_success(self, service, vehicle_repo, user_id, vehicle_id, mock_vehicle):
        dto = EditVehicleDTO(license_plate="new456")
        vehicle_repo.get_by_id.return_value = mock_vehicle
        vehicle_repo.get_by_license_plate.return_value = None
        vehicle_repo.update.return_value = mock_vehicle
        
        result = await service.update_vehicle(user_id, vehicle_id, dto)
        
        assert result == mock_vehicle
        assert mock_vehicle.license_plate == "NEW456"  # Should be uppercase
        vehicle_repo.update.assert_called_once_with(mock_vehicle)


class TestVehicleServiceDeleteVehicle:

    @pytest.fixture
    def user_id(self):
        return uuid4()

    @pytest.fixture
    def vehicle_id(self):
        return uuid4()

    @pytest.fixture
    def vehicle_repo(self):
        return AsyncMock(spec=VehicleRepository)

    @pytest.fixture
    def service(self, vehicle_repo):
        return VehicleService(vehicle_repo)

    @pytest.fixture
    def mock_vehicle(self):
        vehicle = MagicMock(spec=Vehicle)
        vehicle.id = uuid4()
        vehicle.is_active = True
        return vehicle

    @pytest.mark.asyncio
    async def test_delete_vehicle_success(self, service, vehicle_repo, user_id, vehicle_id, mock_vehicle):
        vehicle_repo.get_by_id.return_value = mock_vehicle
        vehicle_repo.delete.return_value = None
        
        await service.delete_vehicle(user_id, vehicle_id)
        
        vehicle_repo.delete.assert_called_once_with(mock_vehicle)

    @pytest.mark.asyncio
    async def test_delete_vehicle_not_found(self, service, vehicle_repo, user_id, vehicle_id):
        vehicle_repo.get_by_id.return_value = None
        
        with pytest.raises(VehicleNotFoundError):
            await service.delete_vehicle(user_id, vehicle_id)