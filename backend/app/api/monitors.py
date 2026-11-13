
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.api.deps import get_current_user
from app.models.user import User

from app.db.database import get_db
from app.schemas.monitor import (
    MonitorCreate,
    MonitorResponse,
    MonitorUpdate,
    MonitorListResponse
)
from app.services.monitor_service import (
    create_monitor_service,
    get_all_monitors_service,
    get_monitor_by_id_service,
    update_monitor_service,
    delete_monitor_service
)


router = APIRouter(
    prefix="/api/v1/monitors",
    tags=["Monitors"]
)


@router.post(
    "/",
    response_model=MonitorResponse,
    status_code=status.HTTP_201_CREATED
)
def create_monitor(
    monitor: MonitorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return create_monitor_service(
            db=db,
            monitor=monitor,
            user_id=current_user.id
        )

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to create monitor due to a database constraint conflict."
        )


@router.get("/", response_model=MonitorListResponse)
def get_all_monitors(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
):
    monitors, total = get_all_monitors_service(
        db=db,
        user_id=current_user.id,
        limit=limit,
        offset=offset
    )

    return {
        "items": monitors,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/{monitor_id}", response_model=MonitorResponse)
def get_monitor_by_id(
    monitor_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    monitor = get_monitor_by_id_service(
        db=db,
        monitor_id=monitor_id,
        user_id=current_user.id
    )

    if monitor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitor not found"
        )

    return monitor


@router.patch("/{monitor_id}", response_model=MonitorResponse)
def update_monitor(
    monitor_id: UUID,
    monitor_update: MonitorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    updated_monitor = update_monitor_service(
        db=db,
        monitor_id=monitor_id,
        monitor_update=monitor_update,
        user_id=current_user.id
    )

    if updated_monitor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitor not found"
        )

    return updated_monitor


@router.delete("/{monitor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_monitor(
    monitor_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = delete_monitor_service(
        db=db,
        monitor_id=monitor_id,
        user_id=current_user.id
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitor not found"
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)