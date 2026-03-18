from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Enum, ForeignKey, JSON, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class DeviceType(str, enum.Enum):
    STARLINK = "starlink"
    MIKROTIK = "mikrotik"


class DeviceStatus(str, enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    UNKNOWN = "unknown"
    ERROR = "error"


class Device(Base):
    """Device model for Starlink dishes and MikroTik routers"""
    __tablename__ = "devices"
    __table_args__ = (
        UniqueConstraint("ip_address", "user_id", name="uq_device_ip_user"),
    )

    id = Column(String, primary_key=True)
    name = Column(String, index=True)
    device_type = Column(Enum(DeviceType), index=True)
    ip_address = Column(String, index=True)
    status = Column(Enum(DeviceStatus), default=DeviceStatus.UNKNOWN)

    # Owner
    user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    owner = relationship("User", back_populates="devices")
    
    # Configuration
    location = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    config = Column(JSON, default={})
    
    # Metrics
    last_latency = Column(Float, nullable=True)
    last_download_speed = Column(Float, nullable=True)
    last_upload_speed = Column(Float, nullable=True)
    cpu_usage = Column(Float, nullable=True)
    memory_usage = Column(Float, nullable=True)
    uptime = Column(Integer, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_seen = Column(DateTime, nullable=True)
    
    # Relationships
    credentials = relationship("DeviceCredentials", back_populates="device", cascade="all, delete-orphan")
    metrics = relationship("DeviceMetrics", back_populates="device", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="device", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Device {self.name} ({self.device_type.value}) - {self.status.value}>"


class DeviceCredentials(Base):
    """Store credentials for devices"""
    __tablename__ = "credentials"
    
    id = Column(String, primary_key=True)
    device_id = Column(String, ForeignKey("devices.id"), nullable=True)
    device = relationship("Device", back_populates="credentials")
    
    # For Starlink: cookie
    # For MikroTik: username & password
    auth_type = Column(String)  # "cookie", "credentials"
    auth_data = Column(JSON)  # Encrypted auth data
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DeviceMetrics(Base):
    """Historical metrics for devices"""
    __tablename__ = "device_metrics"
    
    id = Column(Integer, primary_key=True)
    device_id = Column(String, ForeignKey("devices.id"))
    device = relationship("Device", back_populates="metrics")
    
    # Network metrics
    latency = Column(Float, nullable=True)
    download_speed = Column(Float, nullable=True)
    upload_speed = Column(Float, nullable=True)
    
    # System metrics
    cpu_usage = Column(Float, nullable=True)
    memory_usage = Column(Float, nullable=True)
    disk_usage = Column(Float, nullable=True)
    uptime = Column(Integer, nullable=True)
    
    # Starlink specific
    obstructed_seconds = Column(Integer, nullable=True)
    snr = Column(Float, nullable=True)
    
    # MikroTik specific
    interface_stats = Column(JSON, nullable=True)
    queue_stats = Column(JSON, nullable=True)
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    __tablename__ = "device_metrics"


class Alert(Base):
    """Alerts for device issues"""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True)
    device_id = Column(String, ForeignKey("devices.id"))
    device = relationship("Device", back_populates="alerts")
    
    severity = Column(String)  # "info", "warning", "error", "critical"
    message = Column(Text)
    resolved = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime, nullable=True)
