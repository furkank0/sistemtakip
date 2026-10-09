import ipaddress
from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

AssetType = Literal["domain", "hosting", "vds", "license"]
AssetStatus = Literal["active", "expired", "cancelled"]
CostPeriod = Literal["monthly", "yearly", "one_time", "unspecified"]
TYPE_SPECIFIC_FIELDS: dict[str, frozenset[str]] = {
    "domain": frozenset({"nameservers"}),
    "hosting": frozenset({"hosting_plan", "management_url"}),
    "vds": frozenset({"ip_address", "operating_system", "vcpu_count", "memory_gb", "storage_gb"}),
    "license": frozenset({"product_name", "seat_count"}),
}


def normalize_currency(value: object) -> object:
    if value is None:
        raise ValueError("currency cannot be null")
    return value.strip().upper() if isinstance(value, str) else value


def validate_reminder_day_list(value: list[int] | None) -> list[int] | None:
    if value is not None and (any(days <= 0 for days in value) or len(set(value)) != len(value)):
        raise ValueError("reminder_days must contain unique positive day counts")
    return value


def invalid_asset_type_fields(asset_type: str, values: dict[str, object]) -> list[str]:
    allowed_fields = TYPE_SPECIFIC_FIELDS.get(asset_type, frozenset())
    all_fields = set().union(*TYPE_SPECIFIC_FIELDS.values())
    return [
        field
        for field in all_fields
        if field not in allowed_fields and values.get(field) is not None
    ]


def normalize_nameservers(value: list[str] | None) -> list[str] | None:
    if value is None:
        return None
    nameservers = [server.strip() for server in value]
    if any(
        not server or len(server) > 253 or any(char.isspace() for char in server)
        for server in nameservers
    ):
        raise ValueError("nameservers must be non-blank hostnames")
    return nameservers


def normalize_optional_asset_text(value: str | None) -> str | None:
    cleaned = value.strip() if value is not None else None
    return cleaned or None


def validate_management_url(value: str | None) -> str | None:
    cleaned = normalize_optional_asset_text(value)
    if not cleaned:
        return None
    parsed = urlsplit(cleaned)
    try:
        _ = parsed.port
    except ValueError as error:
        raise ValueError("management_url must be a valid HTTP(S) URL") from error
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("management_url must be a credential-free HTTP(S) URL")
    return cleaned


def normalize_ip_address(value: str | None) -> str | None:
    cleaned = normalize_optional_asset_text(value)
    if not cleaned:
        return None
    try:
        return str(ipaddress.ip_address(cleaned))
    except ValueError as error:
        raise ValueError("ip_address must be a valid IPv4 or IPv6 address") from error


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
    nameservers: list[str] | None = None
    hosting_plan: str | None = Field(default=None, max_length=255)
    management_url: str | None = Field(default=None, max_length=500)
    ip_address: str | None = Field(default=None, max_length=45)
    operating_system: str | None = Field(default=None, max_length=120)
    vcpu_count: int | None = Field(default=None, ge=1, le=1024)
    memory_gb: int | None = Field(default=None, ge=1, le=1048576)
    storage_gb: int | None = Field(default=None, ge=1, le=1048576)
    product_name: str | None = Field(default=None, max_length=255)
    seat_count: int | None = Field(default=None, ge=1, le=1000000)
    notes: str | None = None

    @field_validator("reminder_days")
    @classmethod
    def validate_reminder_days(cls, value: list[int] | None) -> list[int] | None:
        return validate_reminder_day_list(value)

    @field_validator("currency", mode="before")
    @classmethod
    def normalize_currency_code(cls, value: object) -> object:
        return normalize_currency(value)

    @field_validator("nameservers")
    @classmethod
    def normalize_nameservers(cls, value: list[str] | None) -> list[str] | None:
        return normalize_nameservers(value)

    @field_validator("hosting_plan", "operating_system", "product_name")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return normalize_optional_asset_text(value)

    @field_validator("management_url")
    @classmethod
    def validate_management_url(cls, value: str | None) -> str | None:
        return validate_management_url(value)

    @field_validator("ip_address")
    @classmethod
    def validate_ip_address(cls, value: str | None) -> str | None:
        return normalize_ip_address(value)

    @model_validator(mode="after")
    def validate_asset(self) -> "AssetBase":
        if self.starts_at and self.expires_at and self.expires_at < self.starts_at:
            raise ValueError("expires_at must be on or after starts_at")
        invalid_fields = invalid_asset_type_fields(self.type, self.model_dump())
        if invalid_fields:
            raise ValueError(f"fields not supported for {self.type}: {', '.join(invalid_fields)}")
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
    nameservers: list[str] | None = None
    hosting_plan: str | None = Field(default=None, max_length=255)
    management_url: str | None = Field(default=None, max_length=500)
    ip_address: str | None = Field(default=None, max_length=45)
    operating_system: str | None = Field(default=None, max_length=120)
    vcpu_count: int | None = Field(default=None, ge=1, le=1024)
    memory_gb: int | None = Field(default=None, ge=1, le=1048576)
    storage_gb: int | None = Field(default=None, ge=1, le=1048576)
    product_name: str | None = Field(default=None, max_length=255)
    seat_count: int | None = Field(default=None, ge=1, le=1000000)
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

    @field_validator("type")
    @classmethod
    def require_type_when_provided(cls, value: AssetType | None) -> AssetType:
        if value is None:
            raise ValueError("type cannot be null")
        return value

    @field_validator("nameservers")
    @classmethod
    def normalize_nameservers(cls, value: list[str] | None) -> list[str] | None:
        return normalize_nameservers(value)

    @field_validator("hosting_plan", "operating_system", "product_name")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return normalize_optional_asset_text(value)

    @field_validator("management_url")
    @classmethod
    def validate_management_url(cls, value: str | None) -> str | None:
        return validate_management_url(value)

    @field_validator("ip_address")
    @classmethod
    def validate_ip_address(cls, value: str | None) -> str | None:
        return normalize_ip_address(value)

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
    snoozed_until: datetime | None
    sent_at: datetime | None


class NotificationSnoozeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    days: Literal[1, 3, 7]


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
