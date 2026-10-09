from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Asset
from app.schemas import AssetCreate, AssetRead, AssetUpdate

router = APIRouter(prefix="/api/assets", tags=["assets"])


@router.post("", response_model=AssetRead, status_code=status.HTTP_201_CREATED)
def create_asset(payload: AssetCreate, db: Session = Depends(get_db)) -> Asset:  # noqa: B008
    asset = Asset(**payload.model_dump())
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


@router.get("", response_model=list[AssetRead])
def list_assets(
    db: Session = Depends(get_db),  # noqa: B008
    asset_type: str | None = Query(default=None, alias="type"),
    asset_status: str | None = Query(default=None, alias="status"),
) -> list[Asset]:
    query = select(Asset).order_by(Asset.expires_at.asc().nullslast(), Asset.name.asc())
    if asset_type:
        query = query.where(Asset.type == asset_type)
    if asset_status:
        query = query.where(Asset.status == asset_status)
    return list(db.scalars(query).all())


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
    for field, value in values.items():
        setattr(asset, field, value)
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
