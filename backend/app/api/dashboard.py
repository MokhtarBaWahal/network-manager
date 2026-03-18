"""
Dashboard API Endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.device import Device, DeviceType, DeviceStatus, DeviceMetrics, Alert
from app.models.user import User
from app.schemas.device import DashboardStats, DashboardResponse, DeviceResponse, AlertResponse
from app.auth import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get dashboard statistics for the current user"""
    def _count(extra_filter=None):
        q = db.query(func.count(Device.id)).filter(Device.user_id == current_user.id)
        if extra_filter is not None:
            q = q.filter(extra_filter)
        return q.scalar() or 0

    total_devices = _count()
    online_devices = _count(Device.status == DeviceStatus.ONLINE)
    offline_devices = _count(Device.status == DeviceStatus.OFFLINE)
    error_devices = _count(Device.status == DeviceStatus.ERROR)
    starlink_count = _count(Device.device_type == DeviceType.STARLINK)
    mikrotik_count = _count(Device.device_type == DeviceType.MIKROTIK)

    avg_latency = db.query(func.avg(Device.last_latency)).filter(
        Device.user_id == current_user.id,
        Device.last_latency.isnot(None),
    ).scalar()

    avg_download_speed = db.query(func.avg(Device.last_download_speed)).filter(
        Device.user_id == current_user.id,
        Device.last_download_speed.isnot(None),
    ).scalar()

    return DashboardStats(
        total_devices=total_devices,
        online_devices=online_devices,
        offline_devices=offline_devices,
        error_devices=error_devices,
        starlink_count=starlink_count,
        mikrotik_count=mikrotik_count,
        avg_latency=avg_latency,
        avg_download_speed=avg_download_speed,
    )


@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get full dashboard data for the current user"""
    stats_response = await get_dashboard_stats(db, current_user)

    devices = db.query(Device).filter(Device.user_id == current_user.id).all()
    devices_response = [DeviceResponse.model_validate(d) for d in devices]

    recent_alerts = (
        db.query(Alert)
        .join(Device, Alert.device_id == Device.id)
        .filter(Device.user_id == current_user.id, Alert.resolved == False)
        .order_by(Alert.created_at.desc())
        .limit(10)
        .all()
    )
    alerts_response = [AlertResponse.model_validate(a) for a in recent_alerts]

    return DashboardResponse(
        stats=stats_response,
        devices=devices_response,
        recent_alerts=alerts_response,
    )


@router.get("/alerts")
async def get_alerts(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get alerts for the current user's devices"""
    alerts = (
        db.query(Alert)
        .join(Device, Alert.device_id == Device.id)
        .filter(Device.user_id == current_user.id)
        .order_by(Alert.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [AlertResponse.model_validate(a) for a in alerts]


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark an alert as resolved"""
    alert = (
        db.query(Alert)
        .join(Device, Alert.device_id == Device.id)
        .filter(Alert.id == alert_id, Device.user_id == current_user.id)
        .first()
    )
    if not alert:
        return {"success": False, "message": "Alert not found"}

    from datetime import datetime
    alert.resolved = True
    alert.resolved_at = datetime.utcnow()
    db.commit()
    return {"success": True, "message": "Alert marked as resolved"}


@router.get("/metrics/{device_id}")
async def get_device_metrics_history(
    device_id: str,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get historical metrics for a device"""
    device = db.query(Device).filter(
        Device.id == device_id,
        Device.user_id == current_user.id,
    ).first()
    if not device:
        return []

    metrics = (
        db.query(DeviceMetrics)
        .filter(DeviceMetrics.device_id == device_id)
        .order_by(DeviceMetrics.timestamp.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "timestamp": m.timestamp,
            "cpu_usage": m.cpu_usage,
            "memory_usage": m.memory_usage,
            "uptime": m.uptime,
            "latency": m.latency,
            "download_speed": m.download_speed,
            "upload_speed": m.upload_speed,
        }
        for m in metrics
    ]
