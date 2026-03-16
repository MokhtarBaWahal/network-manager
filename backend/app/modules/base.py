from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class DeviceInfo:
    """Standard device information"""
    id: str
    name: str
    status: str  # "online", "offline", "error"
    ip_address: str
    latency: Optional[float] = None
    download_speed: Optional[float] = None
    upload_speed: Optional[float] = None
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    uptime: Optional[int] = None
    last_updated: Optional[datetime] = None


class BaseDeviceDriver(ABC):
    """Abstract base class for device drivers"""
    
    def __init__(self, device_id: str, ip_address: str, credentials: Dict[str, Any]):
        self.device_id = device_id
        self.ip_address = ip_address
        self.credentials = credentials
        self.connected = False
    
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to device"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Close connection to device"""
        pass
    
    @abstractmethod
    async def get_status(self) -> DeviceInfo:
        """Get device status and metrics"""
        pass
    
    @abstractmethod
    async def reboot(self) -> bool:
        """Reboot the device"""
        pass
    
    @abstractmethod
    async def get_config(self) -> Dict[str, Any]:
        """Get device configuration"""
        pass
    
    @abstractmethod
    async def set_config(self, config: Dict[str, Any]) -> bool:
        """Apply configuration to device"""
        pass
    
    async def is_connected(self) -> bool:
        """Check if device is connected"""
        return self.connected
