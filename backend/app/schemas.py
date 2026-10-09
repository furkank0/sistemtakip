from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

AssetType = Literal["domain", "hosting", "vds", "license"]
AssetStatus = Literal["active", "expired", "cancelled"]
CostPeriod = Literal["monthly", "yearly", "one_time", "unspecified"]


def normalize_currency(value: object) -> object:
    if value is None:
        raise ValueError("currency cannot be null")
    return value.strip().upper() if isinstance(value, str) else value


def validate_reminder_day_list(value: list[int] | None) -> list[int] | None:
    if value is not None and (any(days <= 0 for days in value) or len(set(value)) != len(value)):
        raise ValueError("reminder_days must contain unique positive day counts")
    return value


class AssetBase(BaseModel):
    type: AssetType
    name: str = Field(min_length=1, max_length=255)
    vendor: str | None = Field(default=None, max_length=255)
    owner: str | None = Field(default=None, max_length=255)
    cost: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    currency: str = Field(default="TRY", pattern=r"^[A-Z]{3}$")
    cost_period: CostPeriod = "unspecified"
    starts_at: date | None = None
    expires_at: date | None = None
    auto_renew: bool = False
    status: AssetStatus = "active"
    reminder_days: list[int] | None = None
    notes: str | None = None

    @field_validator("reminder_days")
    @classmethod
    def validate_reminder_days(cls, value: list[int] | None) -> list[int] | None:
        return validate_reminder_day_list(value)

    @field_validator("currency", mode="before")
    @classmethod
    def normalize_currency_code(cls, value: object) -> object:
        return normalize_currency(value)

    @model_validator(mode="after")
    def validate_date_range(self) -> "AssetBase":
        if self.starts_at and self.expires_at and self.expires_at < self.starts_at:
            raise ValueError("expires_at must be on or after starts_at")
        return self


class AssetCreate(AssetBase):
    tag_ids: list[int] = Field(default_factory=list)
    contact_ids: list[int] = Field(default_factory=list)
    vendor_id: int | None = Field(default=None, ge=1)


class AssetUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: AssetType | None = None
    name: str | None = Field(default=None, min_length=1, max_length=255)
    vendor: str | None = Field(default=None, max_length=255)
    owner: str | None = Field(default=None, max_length=255)
    cost: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    currency: str | None = Field(default=None, pattern=r"^[A-Z]{3}$")
    cost_period: CostPeriod | None = None
    starts_at: date | None = None
    expires_at: date | None = None
    auto_renew: bool | None = None
    status: AssetStatus | None = None
    reminder_days: list[int] | None = None
    notes: str | None = None
    tag_ids: list[int] | None = None
    contact_ids: list[int] | None = None
    vendor_id: int | None = Field(default=None, ge=1)

    @field_validator("reminder_days")
    @classmethod
    def validate_reminder_days(cls, value: list[int] | None) -> list[int] | None:
        return validate_reminder_day_list(value)

    @field_validator("currency", mode="before")
    @classmethod
    def normalize_currency_code(cls, value: object) -> object:
        return normalize_currency(value)

    @field_validator("cost_period")
    @classmethod
    def require_cost_period_when_provided(cls, value: CostPeriod | None) -> CostPeriod:
        if value is None:
            raise ValueError("cost_period cannot be null")
        return value


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_id: int
    rule: str
    expires_at: date
    channel: str | None
    status: str
    created_at: datetime
    sent_at: datetime | None


class NotificationEvaluation(BaseModel):
    evaluated_on: date
    created_count: int
    notifications: list[NotificationRead]


class TagCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)


class TagRead(TagCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class ContactCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=80)
    role: str | None = Field(default=None, max_length=120)

    @field_validator("name", "email", "phone", "role")
    @classmethod
    def strip_contact_values(cls, value: str | None) -> str | None:
        cleaned = value.strip() if value is not None else None
        if cleaned == "":
            raise ValueError("contact fields cannot be blank")
        return cleaned


class ContactRead(ContactCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class VendorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    support_email: str | None = Field(default=None, max_length=255)
    panel_url: str | None = Field(default=None, max_length=500)


class VendorRead(VendorCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class AssetRead(AssetBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    tags: list[TagRead] = Field(default_factory=list)
    contacts: list[ContactRead] = Field(default_factory=list)
    vendor_id: int | None = None


class AssetList(BaseModel):
    items: list[AssetRead]
    total: int
    offset: int
    limit: int


class CurrencyCostSummary(BaseModel):
    currency: str
    monthly: Decimal
    yearly: Decimal
    one_time: Decimal
    unspecified: Decimal


class DashboardSummary(BaseModel):
    total: int
    active: int
    expired: int
    expiring_30_days: int
    expiring_60_days: int
    expiring_90_days: int
    by_type: dict[str, int]
    costs_by_currency: list[CurrencyCostSummary]


class AuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    actor: str
    action: Literal["create", "update", "delete"]
    entity: str
    entity_id: int
    diff: dict[str, object]
    at: datetime
