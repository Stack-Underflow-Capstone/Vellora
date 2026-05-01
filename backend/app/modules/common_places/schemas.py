import uuid
import datetime
from pydantic import BaseModel
from app.modules.trips.utils.crypto import decrypt_address


class CommonPlaceBase(BaseModel):
    name: str
    address: str


class CommonPlaceCreate(CommonPlaceBase):
    pass


class CommonPlaceUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    

class CommonPlaceResponse(CommonPlaceBase):
    user_id: uuid.UUID
    id: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime

    @classmethod
    def model_validate(cls, place):
        data = {
            "user_id": place.user_id,
            "id": place.id,
            "name": place.name,
            "address": decrypt_address(place.address),
            "created_at": place.created_at,
            "updated_at": place.updated_at,
        }
        return cls(**data)

    class Config:
        from_attributes = True
