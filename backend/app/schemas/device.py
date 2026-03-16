from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class DeviceType(str, Enum):
    STARLINK = "starlink"
    MIKROTIK = "mikrotik"


class DeviceStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    UNKNOWN = "unknown"
    ERROR = "error"


# Device Schemas
class DeviceMetrics(BaseModel):
    latency: Optional[float] = None
    download_speed: Optional[float] = None
    upload_speed: Optional[float] = None
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    disk_usage: Optional[float] = None
    uptime: Optional[int] = None


class DeviceBase(BaseModel):
    name: str
    device_type: DeviceType
    ip_address: str
    location: Optional[str] = None
    description: Optional[str] = None


class DeviceCreate(DeviceBase):
    """Schema for creating a new device"""
    pass


class DeviceUpdate(BaseModel):
    """Schema for updating device"""
    name: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class DeviceResponse(DeviceBase):
    """Schema for device response"""
    id: str
    status: DeviceStatus
    last_latency: Optional[float] = None
    last_download_speed: Optional[float] = None
    last_upload_speed: Optional[float] = None
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    uptime: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    last_seen: Optional[datetime] = None

    class Config:
        from_attributes = True


class DeviceDetailResponse(DeviceResponse):
    """Extended device response with metrics history"""
    config: Dict[str, Any]
    recent_metrics: Optional[list] = None


# Credential Schemas
class CredentialBase(BaseModel):
    auth_type: str  # "cookie" or "credentials"


class StarlinkCredential(CredentialBase):
    """For Starlink: cookie-based auth"""
    cookie: str


class MikroTikCredential(CredentialBase):
    """For MikroTik: username/password auth"""
    username: str
    password: str


# Control Schemas
class RebootRequest(BaseModel):
    device_id: str


class RebootResponse(BaseModel):
    success: bool
    message: str


class ConfigChangeRequest(BaseModel):
    device_id: str
    config: Dict[str, Any]


class ConfigChangeResponse(BaseModel):
    success: bool
    message: str
    applied_config: Dict[str, Any]


# Alert Schemas
class AlertResponse(BaseModel):
    id: int
    device_id: str
    severity: str
    message: str
    resolved: bool
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Dashboard Schemas
class DashboardStats(BaseModel):
    total_devices: int
    online_devices: int
    offline_devices: int
    error_devices: int
    starlink_count: int
    mikrotik_count: int
    avg_latency: Optional[float] = None
    avg_download_speed: Optional[float] = None


class DashboardResponse(BaseModel):
    stats: DashboardStats
    devices: list[DeviceResponse]
    recent_alerts: list[AlertResponse]
