from uuid import UUID
from sqlalchemy.exc import IntegrityError
from app.modules.common_places.repository import CommonPlaceRepo
from app.modules.common_places.schemas import CommonPlaceCreate, CommonPlaceUpdate
from app.modules.common_places.models import CommonPlace
from app.modules.common_places.exceptions import InvalidCommonPlaceDataError, CommonPlaceNotFoundError, DuplicateCommonPlaceError, CommonPlacePersistenceError, MaxCommonPlacesError
from app.modules.trips.utils.crypto import encrypt_address


class CommonPlaceService:
    def __init__(self, commonplace_repo: CommonPlaceRepo):
        self.commonplace_repo = commonplace_repo

    async def create_common_place(self, user_id: UUID, data: CommonPlaceCreate):
        if not data.name.strip():
            raise InvalidCommonPlaceDataError("Name is required")
        
        if not data.address.strip():
            raise InvalidCommonPlaceDataError("Address is required")
        
        # Check if user already has 4 common places
        existing_places = await self.commonplace_repo.get_all_by_user(user_id)
        if len(existing_places) >= 4:
            raise MaxCommonPlacesError("Maximum of 4 common places allowed")
        
        cleaned_name = data.name.strip()
        
        # Check for duplicate name
        existing = await self.commonplace_repo.get_by_user_and_commonplace_name(user_id, cleaned_name)
        if existing:
            raise DuplicateCommonPlaceError("A common place with this name already exists")
        
        try:
            encrypted_address = encrypt_address(data.address.strip())
            
            place = CommonPlace(
                user_id=user_id,
                name=cleaned_name,
                address=encrypted_address
            )
            return await self.commonplace_repo.create(place)
        except IntegrityError as e:
            raise DuplicateCommonPlaceError("A common place with this name already exists") from e
        except Exception as e:
            raise CommonPlacePersistenceError("Unexpected error occurred while saving common place") from e

    async def get_all_common_places(self, user_id: UUID):
        return await self.commonplace_repo.get_all_by_user(user_id)

    async def get_common_place(self, user_id: UUID, place_id: UUID):
        place = await self.commonplace_repo.get_by_id(user_id, place_id)
        
        if not place:
            raise CommonPlaceNotFoundError("Common place not found or not owned by user")
        
        return place

    async def update_common_place(self, user_id: UUID, place_id: UUID, data: CommonPlaceUpdate):
        place = await self.get_common_place(user_id, place_id)
        
        if data.name is not None:
            if not data.name.strip():
                raise InvalidCommonPlaceDataError("Name cannot be empty")
            
            cleaned_name = data.name.strip()
            
            # Check for duplicate name (but allow keeping the same name)
            if cleaned_name != place.name:
                existing = await self.commonplace_repo.get_by_user_and_commonplace_name(user_id, cleaned_name)
                if existing:
                    raise DuplicateCommonPlaceError("A common place with this name already exists")
            
            place.name = cleaned_name
        
        if data.address is not None:
            if not data.address.strip():
                raise InvalidCommonPlaceDataError("Address cannot be empty")
            place.address = encrypt_address(data.address.strip())
        
        try:
            return await self.commonplace_repo.update(place)
        except IntegrityError as e:
            raise DuplicateCommonPlaceError("A common place with this name already exists") from e
        except Exception as e:
            raise CommonPlacePersistenceError("Unexpected error occurred while updating common place") from e

    async def delete_common_place(self, user_id: UUID, place_id: UUID):
        place = await self.get_common_place(user_id, place_id)
        await self.commonplace_repo.delete(place)
