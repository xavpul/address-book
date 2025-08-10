from pydantic import BaseModel, Field


class AddressCreate(BaseModel):
    name: str
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)


class AddressOut(BaseModel):
    id: int
    name: str
    lat: float
    lng: float

    class Config:
        orm_mode = True
