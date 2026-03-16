"""
Device Management API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.core.database import get_db
from app.models.device import Device, DeviceType, DeviceStatus, DeviceMetrics
from app.schemas.device import (
    DeviceCreate,
    DeviceResponse,
    DeviceUpdate,
    DeviceDetailResponse,
    RebootRequest,
    RebootResponse,
    ConfigChangeRequest,
    ConfigChangeResponse,
)
from app.modules.base import BaseDeviceDriver
from app.modules.starlink import StarlinkDriver
from app.modules.mikrotik import MikroTikDriver

router = APIRouter(prefix="/api/devices", tags=["devices"])

# Device driver registry
device_drivers = {}


def get_device_driver(device: Device) -> BaseDeviceDriver:
    """Get or create device driver instance"""
    if device.id not in device_drivers:
        credentials = {}
        if device.credentials:
            credentials = device.credentials.auth_data or {}
        
        if device.device_type == DeviceType.STARLINK:
            device_drivers[device.id] = StarlinkDriver(
                device.id, device.ip_address, credentials
            )
        elif device.device_type == DeviceType.MIKROTIK:
            device_drivers[device.id] = MikroTikDriver(
                device.id, device.ip_address, credentials
            )
    
    return device_drivers[device.id]


@router.get("/", response_model=List[DeviceResponse])
async def list_devices(db: Session = Depends(get_db)):
    """List all devices"""
    devices = db.query(Device).all()
    return devices


@router.get("/{device_id}", response_model=DeviceDetailResponse)
async def get_device(device_id: str, db: Session = Depends(get_db)):
    """Get device details with recent metrics"""
    device = db.query(Device).filter(Device.id == device_id).first()
    
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    
    # TODO: Get recent metrics
    recent_metrics = []
    
    return DeviceDetailResponse(
        **device.__dict__,
        recent_metrics=recent_metrics
    )


@router.post("/", response_model=DeviceResponse)
async def create_device(device_data: DeviceCreate, db: Session = Depends(get_db)):
    """Create a new device"""
    # Check if device already exists
    existing = db.query(Device).filter(Device.ip_address == device_data.ip_address).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Device with this IP address already exists"
        )
    
    # Create new device
    device = Device(
        id=str(uuid.uuid4()),
        name=device_data.name,
        device_type=device_data.device_type,
        ip_address=device_data.ip_address,
        location=device_data.location,
        description=device_data.description,
        status=DeviceStatus.UNKNOWN,
    )
    
    db.add(device)
    db.commit()
    db.refresh(device)
    
    return device


@router.put("/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_id: str,
    device_data: DeviceUpdate,
    db: Session = Depends(get_db)
):
    """Update device information"""
    device = db.query(Device).filter(Device.id == device_id).first()
    
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    
    update_data = device_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(device, field, value)
    
    db.commit()
    db.refresh(device)
    
    return device


@router.delete("/{device_id}")
async def delete_device(device_id: str, db: Session = Depends(get_db)):
    """Delete a device"""
    device = db.query(Device).filter(Device.id == device_id).first()
    
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    
    # Remove driver from registry
    if device_id in device_drivers:
        del device_drivers[device_id]
    
    db.delete(device)
    db.commit()
    
    return {"message": "Device deleted successfully"}


@router.post("/{device_id}/reboot", response_model=RebootResponse)
async def reboot_device(device_id: str, db: Session = Depends(get_db)):
    """Reboot a device"""
    device = db.query(Device).filter(Device.id == device_id).first()
    
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    
    try:
        driver = get_device_driver(device)
        success = await driver.reboot()
        
        if success:
            return RebootResponse(success=True, message=f"Device {device.name} is rebooting")
        else:
            return RebootResponse(success=False, message=f"Failed to reboot {device.name}")
    except Exception as e:
        return RebootResponse(success=False, message=f"Error: {str(e)}")


@router.post("/{device_id}/config", response_model=ConfigChangeResponse)
async def change_device_config(
    device_id: str,
    config_request: ConfigChangeRequest,
    db: Session = Depends(get_db)
):
    """Change device configuration"""
    device = db.query(Device).filter(Device.id == device_id).first()
    
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    
    try:
        driver = get_device_driver(device)
        success = await driver.set_config(config_request.config)
        
        if success:
            # Update device config in database
            device.config = {**(device.config or {}), **config_request.config}
            db.commit()
            
            return ConfigChangeResponse(
                success=True,
                message=f"Configuration applied to {device.name}",
                applied_config=device.config
            )
        else:
            return ConfigChangeResponse(
                success=False,
                message=f"Failed to apply configuration to {device.name}",
                applied_config=device.config or {}
            )
    except Exception as e:
        return ConfigChangeResponse(
            success=False,
            message=f"Error: {str(e)}",
            applied_config=device.config or {}
        )


@router.post("/{device_id}/refresh")
async def refresh_device_status(device_id: str, db: Session = Depends(get_db)):
    """Manually refresh device status"""
    device = db.query(Device).filter(Device.id == device_id).first()
    
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    
    try:
        driver = get_device_driver(device)
        device_info = await driver.get_status()
        
        # Update device in database
        device.status = DeviceStatus(device_info.status)
        device.last_latency = device_info.latency
        device.last_download_speed = device_info.download_speed
        device.last_upload_speed = device_info.upload_speed
        device.cpu_usage = device_info.cpu_usage
        device.memory_usage = device_info.memory_usage
        device.uptime = device_info.uptime
        device.last_seen = device_info.last_updated
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Device {device.name} status refreshed",
            "device": DeviceResponse.model_validate(device)
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }
