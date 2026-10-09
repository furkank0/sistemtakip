from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Table,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


asset_tags = Table(
    "asset_tags",
    Base.metadata,
    Column("asset_id", ForeignKey("assets.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

asset_contacts = Table(
    "asset_contacts",
    Base.metadata,
    Column("asset_id", ForeignKey("assets.id", ondelete="CASCADE"), primary_key=True),
    Column("contact_id", ForeignKey("contacts.id", ondelete="CASCADE"), primary_key=True),
)


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    vendor: Mapped[str] = mapped_column(String(255), nullable=True)
    vendor_id: Mapped[int] = mapped_column(
        ForeignKey("vendors.id", ondelete="SET NULL"), nullable=True, index=True
    )
    owner: Mapped[str] = mapped_column(String(255), nullable=True)
    cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="TRY")
    cost_period: Mapped[str] = mapped_column(
        String(20), nullable=False, default="unspecified", server_default="unspecified"
    )
    starts_at: Mapped[date] = mapped_column(Date, nullable=True)
    expires_at: Mapped[date] = mapped_column(Date, nullable=True, index=True)
    auto_renew: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    reminder_days: Mapped[list[int]] = mapped_column(JSON, nullable=True)
    nameservers: Mapped[list[str]] = mapped_column(JSON, nullable=True)
    hosting_plan: Mapped[str] = mapped_column(String(255), nullable=True)
    management_url: Mapped[str] = mapped_column(String(500), nullable=True)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)
    operating_system: Mapped[str] = mapped_column(String(120), nullable=True)
    vcpu_count: Mapped[int] = mapped_column(Integer, nullable=True)
    memory_gb: Mapped[int] = mapped_column(Integer, nullable=True)
    storage_gb: Mapped[int] = mapped_column(Integer, nullable=True)
    product_name: Mapped[str] = mapped_column(String(255), nullable=True)
    seat_count: Mapped[int] = mapped_column(Integer, nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
    tags: Mapped[list["Tag"]] = relationship(
        secondary=asset_tags, back_populates="assets", order_by="Tag.name"
    )
    contacts: Mapped[list["Contact"]] = relationship(
        secondary=asset_contacts, back_populates="assets", order_by="Contact.name"
    )
    vendor_record: Mapped["Vendor"] = relationship(back_populates="assets")


class Vendor(Base):
    __tablename__ = "vendors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    support_email: Mapped[str] = mapped_column(String(255), nullable=True)
    panel_url: Mapped[str] = mapped_column(String(500), nullable=True)
    assets: Mapped[list[Asset]] = relationship(back_populates="vendor_record")


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    actor: Mapped[str] = mapped_column(String(80), nullable=False)
    action: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    entity: Mapped[str] = mapped_column(String(80), nullable=False)
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    diff: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        # A renewed asset gets a new expiry date and therefore a fresh alert cycle.
        UniqueConstraint(
            "asset_id", "rule", "expires_at", name="uq_notifications_asset_rule_expiry"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    rule: Mapped[str] = mapped_column(String(20), nullable=False)
    expires_at: Mapped[date] = mapped_column(Date, nullable=False)
    channel: Mapped[str] = mapped_column(String(30), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    snoozed_until: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    phone: Mapped[str] = mapped_column(String(80), nullable=True)
    role: Mapped[str] = mapped_column(String(120), nullable=True)
    assets: Mapped[list[Asset]] = relationship(secondary=asset_contacts, back_populates="contacts")


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False, unique=True, index=True)
    assets: Mapped[list[Asset]] = relationship(secondary=asset_tags, back_populates="tags")
