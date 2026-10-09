from datetime import date, datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, tuple_
from sqlalchemy.orm import Session, sessionmaker

from app.database import get_db, get_engine
from app.models import Asset, Notification
from app.schemas import NotificationEvaluation, NotificationRead

DEFAULT_REMINDER_DAYS = (60, 30, 14, 7, 1)
ISTANBUL = ZoneInfo("Europe/Istanbul")

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


def evaluate_renewal_notifications(db: Session, evaluated_on: date) -> list[Notification]:
    assets = db.scalars(
        select(Asset).where(Asset.expires_at.is_not(None), Asset.status != "cancelled")
    ).all()
    due: list[tuple[int, str, date]] = []
    for asset in assets:
        if asset.expires_at is None:
            continue
        days_remaining = (asset.expires_at - evaluated_on).days
        if days_remaining <= 0:
            due.append((asset.id, "expired", asset.expires_at))
            continue
        reminder_days = asset.reminder_days
        thresholds = DEFAULT_REMINDER_DAYS if reminder_days is None else reminder_days
        if days_remaining in thresholds:
            due.append((asset.id, f"days:{days_remaining}", asset.expires_at))

    if not due:
        return []

    existing = set(
        db.execute(
            select(Notification.asset_id, Notification.rule, Notification.expires_at).where(
                tuple_(Notification.asset_id, Notification.rule, Notification.expires_at).in_(due)
            )
        ).tuples()
    )
    created = [
        Notification(asset_id=asset_id, rule=rule, expires_at=expires_at)
        for asset_id, rule, expires_at in due
        if (asset_id, rule, expires_at) not in existing
    ]
    db.add_all(created)
    db.flush()
    return created


def run_daily_renewal_evaluation() -> None:
    session_factory = sessionmaker(bind=get_engine(), autoflush=False, autocommit=False)
    with session_factory() as db:
        evaluate_renewal_notifications(db, datetime.now(ISTANBUL).date())
        db.commit()


@router.get("", response_model=list[NotificationRead])
def list_notifications(
    db: Session = Depends(get_db),  # noqa: B008
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[Notification]:
    query = select(Notification).order_by(Notification.created_at.desc(), Notification.id.desc())
    return list(db.scalars(query.offset(offset).limit(limit)).all())


@router.post("/evaluate", response_model=NotificationEvaluation)
def evaluate_notifications(
    evaluated_on: date | None = Query(default=None, alias="date"),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> NotificationEvaluation:
    current_date = evaluated_on or datetime.now(ISTANBUL).date()
    created = evaluate_renewal_notifications(db, current_date)
    db.commit()
    for notification in created:
        db.refresh(notification)
    return NotificationEvaluation(
        evaluated_on=current_date,
        created_count=len(created),
        notifications=[NotificationRead.model_validate(item) for item in created],
    )
