import pydantic
from typing import Optional


class BaseAdvertisement(pydantic.BaseModel):
    title: str
    description: str
    owner: str

    @pydantic.field_validator("title")
    @classmethod
    def length_title(cls, value: str):
        if len(value) < 5:
            raise ValueError("title is too short")
        return value



class CreateAdvertisement(BaseAdvertisement):
    pass


class UpdateAdvertisement(BaseAdvertisement):
    title: Optional[str] = None
    description: Optional[str] = None
    owner: Optional[str] = None