
from uuid import uuid4, UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.monitor import Monitor
from app.schemas.monitor import MonitorCreate, MonitorUpdate


def create_monitor_service(
    db: Session,
    monitor: MonitorCreate,
    user_id: UUID
):
    new_monitor = Monitor(
        id=uuid4(),
        user_id=user_id,
        name=monitor.name,
        url=str(monitor.url),
        interval=monitor.interval,
        status="active"
    )

    db.add(new_monitor)
    db.commit()
    db.refresh(new_monitor)

    return new_monitor


def get_all_monitors_service(
    db: Session,
    user_id: UUID
):
    statement = select(Monitor).where(
        Monitor.user_id == user_id
    )

    monitors = db.scalars(statement).all()

    return monitors


def get_monitor_by_id_service(
    db: Session,
    monitor_id: UUID,
    user_id: UUID
):
    statement = select(Monitor).where(
        Monitor.id == monitor_id,
        Monitor.user_id == user_id
    )

    monitor = db.scalar(statement)

    return monitor


def update_monitor_service(
    db: Session,
    monitor_id: UUID,
    monitor_update: MonitorUpdate,
    user_id: UUID
):
    existing_monitor = get_monitor_by_id_service(
        db=db,
        monitor_id=monitor_id,
        user_id=user_id
    )

    if existing_monitor is None:
        return None

    update_data = monitor_update.model_dump(
        exclude_unset=True,
        exclude_none=True
    )

    for field, value in update_data.items():

        if field == "url":
            value = str(value)

        setattr(existing_monitor, field, value)

    db.commit()
    db.refresh(existing_monitor)

    return existing_monitor


def delete_monitor_service(
    db: Session,
    monitor_id: UUID,
    user_id: UUID
):
    existing_monitor = get_monitor_by_id_service(
        db=db,
        monitor_id=monitor_id,
        user_id=user_id
    )

    if existing_monitor is None:
        return False

    db.delete(existing_monitor)
    db.commit()

    return True
