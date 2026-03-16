"""
Dashboard API Endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.device import Device, DeviceType, DeviceStatus, Alert
from app.schemas.device import DashboardStats, DashboardResponse, DeviceResponse, AlertResponse

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    
    total_devices = db.query(func.count(Device.id)).scalar() or 0
    online_devices = db.query(func.count(Device.id)).filter(
        Device.status == DeviceStatus.ONLINE
    ).scalar() or 0
    offline_devices = db.query(func.count(Device.id)).filter(
        Device.status == DeviceStatus.OFFLINE
    ).scalar() or 0
    error_devices = db.query(func.count(Device.id)).filter(
        Device.status == DeviceStatus.ERROR
    ).scalar() or 0
    
    starlink_count = db.query(func.count(Device.id)).filter(
        Device.device_type == DeviceType.STARLINK
    ).scalar() or 0
    mikrotik_count = db.query(func.count(Device.id)).filter(
        Device.device_type == DeviceType.MIKROTIK
    ).scalar() or 0
    
    # Calculate average metrics
    avg_latency = db.query(func.avg(Device.last_latency)).filter(
        Device.last_latency.isnot(None)
    ).scalar()
    
    avg_download_speed = db.query(func.avg(Device.last_download_speed)).filter(
        Device.last_download_speed.isnot(None)
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
async def get_dashboard(db: Session = Depends(get_db)):
    """Get full dashboard data"""
    
    # Get stats
    stats_response = await get_dashboard_stats(db)
    
    # Get all devices
    devices = db.query(Device).all()
    devices_response = [DeviceResponse.model_validate(d) for d in devices]
    
    # Get recent alerts
    recent_alerts = db.query(Alert).filter(
        Alert.resolved == False
    ).order_by(Alert.created_at.desc()).limit(10).all()
    alerts_response = [AlertResponse.model_validate(a) for a in recent_alerts]
    
    return DashboardResponse(
        stats=stats_response,
        devices=devices_response,
        recent_alerts=alerts_response,
    )


@router.get("/alerts")
async def get_alerts(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """Get alerts"""
    alerts = db.query(Alert).order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()
    return [AlertResponse.model_validate(a) for a in alerts]


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    """Mark an alert as resolved"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    
    if not alert:
        return {"success": False, "message": "Alert not found"}
    
    from datetime import datetime
    alert.resolved = True
    alert.resolved_at = datetime.utcnow()
    db.commit()
    
    return {"success": True, "message": "Alert marked as resolved"}
