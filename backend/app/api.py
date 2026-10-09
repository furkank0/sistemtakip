import csv
import json
from collections import Counter
from datetime import date, timedelta
from decimal import Decimal
from io import StringIO
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Asset, AuditLog, Contact, Tag, Vendor
from app.schemas import (
    AssetCreate,
    AssetList,
    AssetRead,
    AssetUpdate,
    AuditLogRead,
    ContactCreate,
    ContactRead,
    CurrencyCostSummary,
    DashboardSummary,
    TagCreate,
    TagRead,
    VendorCreate,
    VendorRead,
)

router = APIRouter(prefix="/api/assets", tags=["assets"])
tag_router = APIRouter(prefix="/api/tags", tags=["tags"])
vendor_router = APIRouter(prefix="/api/vendors", tags=["vendors"])
contact_router = APIRouter(prefix="/api/contacts", tags=["contacts"])
audit_router = APIRouter(prefix="/api/audit-log", tags=["audit"])

AUDIT_ACTOR = "anonymous"
AssetSortField = Literal["name", "type", "expires_at", "status"]
SortDirection = Literal["asc", "desc"]
AUDIT_FIELDS = (
    "type",
    "name",
    "vendor",
    "vendor_id",
    "owner",
    "cost",
    "currency",
    "cost_period",
    "starts_at",
    "expires_at",
    "auto_renew",
    "status",
    "reminder_days",
)

CSV_HEADERS = (
    "id",
    "type",
    "name",
    "vendor",
    "owner",
    "cost",
    "currency",
    "cost_period",
    "starts_at",
    "expires_at",
    "auto_renew",
    "status",
    "reminder_days",
    "notes",
    "tags",
    "contacts",
)


def resolve_tags(db: Session, tag_ids: list[int]) -> list[Tag]:
    if not tag_ids:
        return []
    unique_ids = set(tag_ids)
    tags = list(db.scalars(select(Tag).where(Tag.id.in_(unique_ids))).all())
    if len(tags) != len(unique_ids):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Unknown tag")
    return tags


def resolve_contacts(db: Session, contact_ids: list[int]) -> list[Contact]:
    if not contact_ids:
        return []
    unique_ids = set(contact_ids)
    contacts = list(db.scalars(select(Contact).where(Contact.id.in_(unique_ids))).all())
    if len(contacts) != len(unique_ids):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Unknown contact"
        )
    return contacts


def resolve_vendor(db: Session, vendor_id: int | None) -> Vendor | None:
    if vendor_id is None:
        return None
    vendor = db.get(Vendor, vendor_id)
    if vendor is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Unknown vendor"
        )
    return vendor


def asset_snapshot(asset: Asset) -> dict[str, object]:
    snapshot: dict[str, object] = {field: getattr(asset, field) for field in AUDIT_FIELDS}
    for field, value in snapshot.items():
        if isinstance(value, date | Decimal):
            snapshot[field] = str(value)
    snapshot["tag_ids"] = sorted(tag.id for tag in asset.tags)
    snapshot["contact_ids"] = sorted(contact.id for contact in asset.contacts)
    return snapshot


def record_asset_audit(db: Session, action: str, asset: Asset, diff: dict[str, object]) -> None:
    db.add(
        AuditLog(
            actor=AUDIT_ACTOR,
            action=action,
            entity="asset",
            entity_id=asset.id,
            diff=diff,
        )
    )


@router.post("", response_model=AssetRead, status_code=status.HTTP_201_CREATED)
def create_asset(payload: AssetCreate, db: Session = Depends(get_db)) -> Asset:  # noqa: B008
    values = payload.model_dump(exclude={"tag_ids", "contact_ids", "vendor_id", "vendor"})
    vendor = resolve_vendor(db, payload.vendor_id)
    asset = Asset(
        **values,
        vendor_id=payload.vendor_id,
        vendor=vendor.name if vendor else payload.vendor,
        tags=resolve_tags(db, payload.tag_ids),
        contacts=resolve_contacts(db, payload.contact_ids),
    )
    db.add(asset)
    db.flush()
    record_asset_audit(db, "create", asset, {"created": asset_snapshot(asset)})
    db.commit()
    db.refresh(asset)
    return asset


@router.get("", response_model=AssetList)
def list_assets(
    db: Session = Depends(get_db),  # noqa: B008
    asset_type: str | None = Query(default=None, alias="type"),
    asset_status: str | None = Query(default=None, alias="status"),
    tag_id: int | None = Query(default=None, ge=1),
    vendor_id: int | None = Query(default=None, ge=1),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    search: str | None = Query(default=None, max_length=255),
    sort_by: AssetSortField = Query(default="expires_at"),  # noqa: B008
    sort_direction: SortDirection = Query(default="asc"),  # noqa: B008
) -> AssetList:
    query = select(Asset)
    if asset_type:
        query = query.where(Asset.type == asset_type)
    if asset_status:
        query = query.where(Asset.status == asset_status)
    if tag_id:
        query = query.join(Asset.tags).where(Tag.id == tag_id)
    if vendor_id:
        query = query.where(Asset.vendor_id == vendor_id)
    if search:
        search_term = search.strip().lower()
        if search_term:
            query = query.where(
                or_(
                    func.lower(Asset.name).contains(search_term, autoescape=True),
                    func.lower(Asset.vendor).contains(search_term, autoescape=True),
                    func.lower(Asset.owner).contains(search_term, autoescape=True),
                )
            )

    total = int(db.scalar(select(func.count()).select_from(query.order_by(None).subquery())) or 0)
    actual_offset = min(offset, ((total - 1) // limit) * limit) if total else 0
    sort_column = {
        "name": Asset.name,
        "type": Asset.type,
        "expires_at": Asset.expires_at,
        "status": Asset.status,
    }[sort_by]
    sort_order = sort_column.asc() if sort_direction == "asc" else sort_column.desc()
    query = query.order_by(sort_order.nullslast(), Asset.name.asc(), Asset.id.asc())
    assets = list(db.scalars(query.offset(actual_offset).limit(limit)).unique().all())
    return AssetList(
        items=[AssetRead.model_validate(asset) for asset in assets],
        total=total,
        offset=actual_offset,
        limit=limit,
    )


@router.get("/export.csv", response_class=Response)
def export_assets_csv(
    db: Session = Depends(get_db),  # noqa: B008
    asset_type: str | None = Query(default=None, alias="type"),
    asset_status: str | None = Query(default=None, alias="status"),
    tag_id: int | None = Query(default=None, ge=1),
    vendor_id: int | None = Query(default=None, ge=1),
) -> Response:
    query = select(Asset).order_by(Asset.expires_at.asc().nullslast(), Asset.name.asc())
    if asset_type:
        query = query.where(Asset.type == asset_type)
    if asset_status:
        query = query.where(Asset.status == asset_status)
    if tag_id:
        query = query.join(Asset.tags).where(Tag.id == tag_id)
    if vendor_id:
        query = query.where(Asset.vendor_id == vendor_id)

    output = StringIO(newline="")
    writer = csv.writer(output, lineterminator="\r\n")
    writer.writerow(CSV_HEADERS)
    for asset in db.scalars(query):
        writer.writerow(
            (
                asset.id,
                asset.type,
                asset.name,
                asset.vendor or "",
                asset.owner or "",
                asset.cost or "",
                asset.currency,
                asset.cost_period,
                asset.starts_at or "",
                asset.expires_at or "",
                asset.auto_renew,
                asset.status,
                json.dumps(asset.reminder_days) if asset.reminder_days is not None else "",
                asset.notes or "",
                "|".join(tag.name for tag in asset.tags),
                "|".join(contact.name for contact in asset.contacts),
            )
        )

    filename = f"assets-{date.today().isoformat()}.csv"
    return Response(
        content=output.getvalue().encode("utf-8-sig"),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/dashboard", response_model=DashboardSummary)
def dashboard(db: Session = Depends(get_db)) -> DashboardSummary:  # noqa: B008
    assets = list(db.scalars(select(Asset)).all())
    today = date.today()

    def expiring_within(days: int) -> int:
        deadline = today + timedelta(days=days)
        return sum(
            1
            for asset in assets
            if asset.status == "active"
            and asset.expires_at is not None
            and today <= asset.expires_at <= deadline
        )

    return DashboardSummary(
        total=len(assets),
        active=sum(asset.status == "active" for asset in assets),
        expired=sum(
            asset.status == "expired" or (asset.expires_at is not None and asset.expires_at < today)
            for asset in assets
        ),
        expiring_30_days=expiring_within(30),
        expiring_60_days=expiring_within(60),
        expiring_90_days=expiring_within(90),
        by_type=dict(Counter(asset.type for asset in assets)),
        costs_by_currency=build_cost_summaries(assets),
    )


def build_cost_summaries(assets: list[Asset]) -> list[CurrencyCostSummary]:
    costs: dict[str, CurrencyCostSummary] = {}
    for asset in assets:
        if asset.cost is None:
            continue
        summary = costs.setdefault(
            asset.currency,
            CurrencyCostSummary(
                currency=asset.currency,
                monthly=Decimal(0),
                yearly=Decimal(0),
                one_time=Decimal(0),
                unspecified=Decimal(0),
            ),
        )
        if asset.cost_period == "monthly":
            summary.monthly += asset.cost
            summary.yearly += asset.cost * 12
        elif asset.cost_period == "yearly":
            summary.monthly += asset.cost / 12
            summary.yearly += asset.cost
        elif asset.cost_period == "one_time":
            summary.one_time += asset.cost
        else:
            summary.unspecified += asset.cost

    return [costs[currency] for currency in sorted(costs)]


@audit_router.get("", response_model=list[AuditLogRead])
def list_audit_log(
    db: Session = Depends(get_db),  # noqa: B008
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[AuditLog]:
    query = select(AuditLog).order_by(AuditLog.at.desc(), AuditLog.id.desc())
    return list(db.scalars(query.offset(offset).limit(limit)).all())


@tag_router.get("", response_model=list[TagRead])
def list_tags(db: Session = Depends(get_db)) -> list[Tag]:  # noqa: B008
    return list(db.scalars(select(Tag).order_by(Tag.name.asc())).all())


@tag_router.post("", response_model=TagRead, status_code=status.HTTP_201_CREATED)
def create_tag(payload: TagCreate, db: Session = Depends(get_db)) -> Tag:  # noqa: B008
    tag = Tag(name=payload.name.strip())
    if not tag.name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Tag name is required"
        )
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


@vendor_router.get("", response_model=list[VendorRead])
def list_vendors(db: Session = Depends(get_db)) -> list[Vendor]:  # noqa: B008
    return list(db.scalars(select(Vendor).order_by(Vendor.name.asc())).all())


@vendor_router.post("", response_model=VendorRead, status_code=status.HTTP_201_CREATED)
def create_vendor(payload: VendorCreate, db: Session = Depends(get_db)) -> Vendor:  # noqa: B008
    vendor = Vendor(**payload.model_dump())
    vendor.name = vendor.name.strip()
    if not vendor.name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Vendor name is required"
        )
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return vendor


@vendor_router.delete("/{vendor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vendor(vendor_id: int, db: Session = Depends(get_db)) -> None:  # noqa: B008
    vendor = db.get(Vendor, vendor_id)
    if vendor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")
    db.delete(vendor)
    db.commit()


@contact_router.get("", response_model=list[ContactRead])
def list_contacts(db: Session = Depends(get_db)) -> list[Contact]:  # noqa: B008
    return list(db.scalars(select(Contact).order_by(Contact.name.asc(), Contact.id.asc())).all())


@contact_router.post("", response_model=ContactRead, status_code=status.HTTP_201_CREATED)
def create_contact(payload: ContactCreate, db: Session = Depends(get_db)) -> Contact:  # noqa: B008
    contact = Contact(**payload.model_dump())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


@contact_router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(contact_id: int, db: Session = Depends(get_db)) -> None:  # noqa: B008
    contact = db.get(Contact, contact_id)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    db.delete(contact)
    db.commit()


@tag_router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(tag_id: int, db: Session = Depends(get_db)) -> None:  # noqa: B008
    tag = db.get(Tag, tag_id)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    db.delete(tag)
    db.commit()


@router.get("/{asset_id}", response_model=AssetRead)
def get_asset(asset_id: int, db: Session = Depends(get_db)) -> Asset:  # noqa: B008
    asset = db.get(Asset, asset_id)
    if asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    return asset


@router.patch("/{asset_id}", response_model=AssetRead)
def update_asset(  # noqa: B008
    asset_id: int,
    payload: AssetUpdate,
    db: Session = Depends(get_db),  # noqa: B008
) -> Asset:
    asset = get_asset(asset_id, db)
    original = asset_snapshot(asset)
    original_notes = asset.notes
    values = payload.model_dump(exclude_unset=True)
    tag_ids = values.pop("tag_ids", None)
    contact_ids = values.pop("contact_ids", None)
    vendor_id = values.pop("vendor_id", None)
    for field, value in values.items():
        setattr(asset, field, value)
    if tag_ids is not None:
        asset.tags = resolve_tags(db, tag_ids)
    if contact_ids is not None:
        asset.contacts = resolve_contacts(db, contact_ids)
    if "vendor_id" in payload.model_fields_set:
        vendor = resolve_vendor(db, vendor_id)
        asset.vendor_id = vendor_id
        asset.vendor = vendor.name if vendor else None  # type: ignore[assignment]
    if asset.starts_at and asset.expires_at and asset.expires_at < asset.starts_at:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="expires_at must be on or after starts_at",
        )
    updated = asset_snapshot(asset)
    diff: dict[str, object] = {
        field: {"old": original[field], "new": updated[field]}
        for field in original
        if original[field] != updated[field]
    }
    if asset.notes != original_notes:
        diff["notes"] = {"changed": True}
    if diff:
        record_asset_audit(db, "update", asset, diff)
    db.commit()
    db.refresh(asset)
    return asset


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(asset_id: int, db: Session = Depends(get_db)) -> None:  # noqa: B008
    asset = get_asset(asset_id, db)
    record_asset_audit(db, "delete", asset, {"deleted": asset_snapshot(asset)})
    db.delete(asset)
    db.commit()
