from decimal import Decimal
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class SPackageTypes(str, Enum):
    CLOTHES = 'одежда'
    ELECTRONICS = 'электроника'
    OTHER = 'разное'


class SPackageTypeNew(BaseModel):
    name: SPackageTypes


class SPackageType(SPackageTypeNew):
    id: int

    model_config = ConfigDict(from_attributes=True)


class SPackageNew(BaseModel):
    title: str = Field(..., description="Название посылки")
    weight: int = Field(..., description="Вес посылки в граммах")
    package_type_id: int = Field(..., description="Идентификатор типа посылки")
    cost_of_contents: Decimal = Field(..., description="Стоимость содержимого посылки в долларах")


class SPackage(BaseModel):
    id: int
    title: str = Field(..., description="Название посылки")
    weight: int = Field(..., description="Вес посылки в граммах")
    package_type: SPackageType
    cost_of_contents: Decimal = Field(..., description="Стоимость содержимого посылки в долларах")
    price: Optional[Decimal] = Field(None, description="Стоимость доставки")
    user_session_id: str

    model_config = ConfigDict(from_attributes=True)


class SPackageCheck(BaseModel):
    id: int
    title: str = Field(..., description="Название посылки")
    weight: int = Field(..., description="Вес посылки в граммах")
    cost_of_contents: Decimal = Field(..., description="Стоимость содержимого посылки в долларах")
    price: Optional[Decimal] = Field(None, description="Стоимость доставки")
    user_session_id: str

    model_config = ConfigDict(from_attributes=True)


class PackageFilters:
    def __init__(self,
                 package_type: str | None = None,
                 is_price_count: bool | None = None):
        self.package_type = package_type
        self.is_price_count = is_price_count

    def to_dict(self) -> dict:
        data = {'package_type': self.package_type, 'is_price_count': self.is_price_count}
        filtered_data = {key: value for key, value in data.items() if value is not None}
        return filtered_data
