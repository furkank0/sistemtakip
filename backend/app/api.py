import csv
from collections import Counter
from datetime import date, timedelta
from io import StringIO

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Asset, Tag, Vendor
from app.schemas import (
    AssetCreate,
    AssetList,
    AssetRead,
    AssetUpdate,
    DashboardSummary,
    TagCreate,
    TagRead,
    VendorCreate,
    VendorRead,
)

router = APIRouter(prefix="/api/assets", tags=["assets"])
tag_router = APIRouter(prefix="/api/tags", tags=["tags"])
vendor_router = APIRouter(prefix="/api/vendors", tags=["vendors"])

CSV_HEADERS = (
    "id",
    "type",
    "name",
    "vendor",
    "owner",
    "cost",
    "currency",
    "starts_at",
    "expires_at",
    "auto_renew",
    "status",
    "notes",
    "tags",
)


def resolve_tags(db: Session, tag_ids: list[int]) -> list[Tag]:
    if not tag_ids:
        return []
    unique_ids = set(tag_ids)
    tags = list(db.scalars(select(Tag).where(Tag.id.in_(unique_ids))).all())
    if len(tags) != len(unique_ids):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Unknown tag")
    return tags


def resolve_vendor(db: Session, vendor_id: int | None) -> Vendor | None:
    if vendor_id is None:
        return None
    vendor = db.get(Vendor, vendor_id)
    if vendor is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Unknown vendor"
        )
    return vendor


@router.post("", response_model=AssetRead, status_code=status.HTTP_201_CREATED)
def create_asset(payload: AssetCreate, db: Session = Depends(get_db)) -> Asset:  # noqa: B008
    values = payload.model_dump(exclude={"tag_ids", "vendor_id", "vendor"})
    vendor = resolve_vendor(db, payload.vendor_id)
    asset = Asset(
        **values,
        vendor_id=payload.vendor_id,
        vendor=vendor.name if vendor else payload.vendor,
        tags=resolve_tags(db, payload.tag_ids),
    )
    db.add(asset)
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
) -> AssetList:
    query = select(Asset).order_by(Asset.expires_at.asc().nullslast(), Asset.name.asc())
    if asset_type:
        query = query.where(Asset.type == asset_type)
    if asset_status:
        query = query.where(Asset.status == asset_status)
    if tag_id:
        query = query.join(Asset.tags).where(Tag.id == tag_id)
    if vendor_id:
        query = query.where(Asset.vendor_id == vendor_id)
    assets = list(db.scalars(query).all())
    return AssetList(
        items=assets[offset : offset + limit], total=len(assets), offset=offset, limit=limit
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
                asset.starts_at or "",
                asset.expires_at or "",
                asset.auto_renew,
                asset.status,
                asset.notes or "",
                "|".join(tag.name for tag in asset.tags),
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
    )


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
    values = payload.model_dump(exclude_unset=True)
    tag_ids = values.pop("tag_ids", None)
    vendor_id = values.pop("vendor_id", None)
    for field, value in values.items():
        setattr(asset, field, value)
    if tag_ids is not None:
        asset.tags = resolve_tags(db, tag_ids)
    if "vendor_id" in payload.model_fields_set:
        vendor = resolve_vendor(db, vendor_id)
        asset.vendor_id = vendor_id
        asset.vendor = vendor.name if vendor else None
    if asset.starts_at and asset.expires_at and asset.expires_at < asset.starts_at:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="expires_at must be on or after starts_at",
        )
    db.commit()
    db.refresh(asset)
    return asset


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(asset_id: int, db: Session = Depends(get_db)) -> None:  # noqa: B008
    asset = get_asset(asset_id, db)
    db.delete(asset)
    db.commit()
