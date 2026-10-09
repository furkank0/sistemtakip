from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

AssetType = Literal["domain", "hosting", "vds", "license"]
AssetStatus = Literal["active", "expired", "cancelled"]


class AssetBase(BaseModel):
    type: AssetType
    name: str = Field(min_length=1, max_length=255)
    vendor: str | None = Field(default=None, max_length=255)
    owner: str | None = Field(default=None, max_length=255)
    cost: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    currency: str = Field(default="TRY", min_length=3, max_length=3)
    starts_at: date | None = None
    expires_at: date | None = None
    auto_renew: bool = False
    status: AssetStatus = "active"
    notes: str | None = None

    @model_validator(mode="after")
    def validate_date_range(self) -> "AssetBase":
        if self.starts_at and self.expires_at and self.expires_at < self.starts_at:
            raise ValueError("expires_at must be on or after starts_at")
        return self


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: AssetType | None = None
    name: str | None = Field(default=None, min_length=1, max_length=255)
    vendor: str | None = Field(default=None, max_length=255)
    owner: str | None = Field(default=None, max_length=255)
    cost: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    starts_at: date | None = None
    expires_at: date | None = None
    auto_renew: bool | None = None
    status: AssetStatus | None = None
    notes: str | None = None


class AssetRead(AssetBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class AssetList(BaseModel):
    items: list[AssetRead]
    total: int
    offset: int
    limit: int


class DashboardSummary(BaseModel):
    total: int
    active: int
    expired: int
    expiring_30_days: int
    expiring_60_days: int
    expiring_90_days: int
    by_type: dict[str, int]
