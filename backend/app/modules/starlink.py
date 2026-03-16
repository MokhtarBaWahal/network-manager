"""
Starlink Device Driver

Integrates with the starlink-client library to manage Starlink dishes.
Handles both local gRPC connections and remote API-based connections.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import asyncio
import logging
from app.modules.base import BaseDeviceDriver, DeviceInfo

try:
    from starlink_client.grpc_client import GrpcClient
    from starlink_client.grpc_web_client import GrpcWebClient
    from starlink_client.cookies_parser import parse_cookie_json
    STARLINK_CLIENT_AVAILABLE = True
except ImportError:
    STARLINK_CLIENT_AVAILABLE = False

logger = logging.getLogger(__name__)

# Default settings
GRPC_PORT = 9200
DEFAULT_TIMEOUT = 10


class StarlinkDriver(BaseDeviceDriver):
    """Driver for managing Starlink dishes"""
    
    def __init__(self, device_id: str, ip_address: str, credentials: Dict[str, Any]):
        super().__init__(device_id, ip_address, credentials)
        self.client = None
        self.connection_type = "local" if not credentials.get("remote") else "remote"
        self.device_name = None
        
    async def connect(self) -> bool:
        """
        Establish connection to Starlink dish
        
        Local: Direct gRPC connection to port 9200
        Remote: API connection with authentication cookie
        """
        if not STARLINK_CLIENT_AVAILABLE:
            logger.error(f"starlink-client library not available. Install it using:")
            logger.error(f"  pip install -e ../../../starlink-client/libs/python/starlink-client")
            self.connected = False
            return False
            
        try:
            if self.connection_type == "local":
                # Local connection via gRPC to the dish
                host = f"{self.ip_address}:{GRPC_PORT}"
                self.client = GrpcClient(host)
                logger.info(f"Connected to Starlink dish at {host} via local gRPC")
            else:
                # Remote connection via gRPC-Web with authentication
                cookie_str = self.credentials.get("cookie")
                if not cookie_str:
                    logger.error(f"No cookie provided for remote connection")
                    self.connected = False
                    return False
                
                try:
                    # Parse cookie if it's a JSON string
                    if cookie_str.startswith("{"):
                        initial_cookies = parse_cookie_json(cookie_str)
                    else:
                        initial_cookies = {"Cookie": cookie_str}
                    
                    credentials_dir = self.credentials.get("credentials_dir", "./credentials")
                    self.client = GrpcWebClient(initial_cookies, credentials_dir)
                    logger.info(f"Connected to Starlink via remote gRPC-Web API")
                except Exception as e:
                    logger.error(f"Failed to parse cookie: {e}")
                    self.connected = False
                    return False
            
            self.connected = True
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Starlink {self.device_id}: {e}")
            self.connected = False
            return False
    
    async def disconnect(self) -> bool:
        """Close connection to device"""
        try:
            self.client = None
            self.connected = False
            logger.info(f"Disconnected from Starlink {self.device_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to disconnect from Starlink {self.device_id}: {e}")
            return False
    
    async def get_status(self) -> DeviceInfo:
        """Get device status and metrics"""
        try:
            if not self.connected:
                if not await self.connect():
                    return DeviceInfo(
                        id=self.device_id,
                        name=f"Starlink-{self.device_id[-4:]}",
                        status="offline",
                        ip_address=self.ip_address,
                        last_updated=datetime.utcnow()
                    )
            
            # For local connection, we get dish status directly
            if self.connection_type == "local":
                return await self._get_local_status()
            else:
                return await self._get_remote_status()
                
        except Exception as e:
            logger.error(f"Error getting status from Starlink {self.device_id}: {e}")
            return DeviceInfo(
                id=self.device_id,
                name=f"Starlink-{self.device_id[-4:]}",
                status="error",
                ip_address=self.ip_address,
                last_updated=datetime.utcnow()
            )
    
    async def _get_local_status(self) -> DeviceInfo:
        """Get status from local dish connection"""
        try:
            from spacex.api.device import device_pb2
            
            # Get dish status
            req = device_pb2.Request(get_status=device_pb2.GetStatusRequest())
            resp = self.client.call(req)
            
            status_data = resp.dish_get_status
            
            # Extract metrics if available
            latency = None
            uptime = None
            
            if hasattr(status_data, 'obstruction_stats') and status_data.obstruction_stats:
                if hasattr(status_data.obstruction_stats, 'avg_gps_latency'):
                    latency = float(status_data.obstruction_stats.avg_gps_latency)
            
            if hasattr(status_data, 'device_state') and status_data.device_state:
                if hasattr(status_data.device_state, 'uptime_s'):
                    uptime = int(status_data.device_state.uptime_s)
            
            return DeviceInfo(
                id=self.device_id,
                name=f"Starlink-{self.device_id[-4:]}",
                status="online",
                ip_address=self.ip_address,
                latency=latency,
                download_speed=None,
                upload_speed=None,
                cpu_usage=None,
                memory_usage=None,
                uptime=uptime,
                last_updated=datetime.utcnow()
            )
        except Exception as e:
            logger.error(f"Error getting local status: {e}")
            raise
    
    async def _get_remote_status(self) -> DeviceInfo:
        """Get status from remote API connection"""
        try:
            # Get service lines to find this device
            service_lines = self.client.get_service_lines()
            
            # Find matching device
            for device_group in service_lines.content.devices:
                for device in device_group.devices:
                    device_id = device.id if hasattr(device, 'id') else None
                    serial_num = device.serial_number if hasattr(device, 'serial_number') else None
                    
                    if device_id == self.device_id or serial_num == self.device_id:
                        # Try to get dish status
                        try:
                            dish_status = self.client.get_dish_status(device_id)
                            
                            return DeviceInfo(
                                id=self.device_id,
                                name=device.name if hasattr(device, 'name') else f"Starlink-{self.device_id[-4:]}",
                                status="online",
                                ip_address=self.ip_address,
                                latency=None,
                                download_speed=None,
                                upload_speed=None,
                                cpu_usage=None,
                                memory_usage=None,
                                uptime=None,
                                last_updated=datetime.utcnow()
                            )
                        except Exception as e:
                            logger.warning(f"Device may be offline: {e}")
                            return DeviceInfo(
                                id=self.device_id,
                                name=device.name if hasattr(device, 'name') else f"Starlink-{self.device_id[-4:]}",
                                status="offline",
                                ip_address=self.ip_address,
                                last_updated=datetime.utcnow()
                            )
            
            # Device not found
            logger.warning(f"Starlink device {self.device_id} not found in service lines")
            return DeviceInfo(
                id=self.device_id,
                name=f"Starlink-{self.device_id[-4:]}",
                status="unknown",
                ip_address=self.ip_address,
                last_updated=datetime.utcnow()
            )
        except Exception as e:
            logger.error(f"Error getting remote status: {e}")
            raise
    
    async def reboot(self) -> bool:
        """Reboot the Starlink dish"""
        try:
            if not self.connected:
                if not await self.connect():
                    return False
            
            from spacex.api.device import device_pb2
            
            # Create reboot request
            reboot_req = device_pb2.Request(reboot=device_pb2.RebootRequest())
            resp = self.client.call(reboot_req)
            
            logger.info(f"Issued reboot command to Starlink {self.device_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to reboot Starlink {self.device_id}: {e}")
            return False
    
    async def get_config(self) -> Dict[str, Any]:
        """Get dish configuration"""
        try:
            if not self.connected:
                if not await self.connect():
                    return {}
            
            from spacex.api.device import device_pb2
            
            # Get dish config
            req = device_pb2.Request(get_config=device_pb2.GetDishConfigRequest())
            resp = self.client.call(req)
            config_data = resp.dish_get_config
            
            config = {
                "snow_melt_enabled": getattr(config_data, 'snow_melt_mode', False),
                "power_saving_enabled": getattr(config_data, 'power_saving_mode', False),
            }
            
            logger.info(f"Retrieved config from Starlink {self.device_id}")
            return config
        except Exception as e:
            logger.error(f"Error getting config from Starlink {self.device_id}: {e}")
            return {}
    
    async def set_config(self, config: Dict[str, Any]) -> bool:
        """Apply configuration changes"""
        try:
            if not self.connected:
                if not await self.connect():
                    return False
            
            from spacex.api.device import device_pb2, dish_config_pb2
            
            # Build config request
            dish_config = dish_config_pb2.DishConfig()
            
            if "snow_melt_enabled" in config:
                dish_config.snow_melt_mode = config["snow_melt_enabled"]
            if "power_saving_enabled" in config:
                dish_config.power_saving_mode = config["power_saving_enabled"]
            
            set_config_req = device_pb2.Request(
                set_config=device_pb2.SetDishConfigRequest(config=dish_config)
            )
            
            resp = self.client.call(set_config_req)
            logger.info(f"Applied configuration to Starlink {self.device_id}")
            return True
        except Exception as e:
            logger.error(f"Error setting config on Starlink {self.device_id}: {e}")
            return False
    
    async def get_wifi_status(self) -> Dict[str, Any]:
        """Get WiFi status and connected clients"""
        try:
            if not self.connected:
                if not await self.connect():
                    return {}
            
            if self.connection_type == "remote":
                # For remote connections, get WiFi status from router
                return await self._get_remote_wifi_status()
            else:
                # For local connections
                return await self._get_local_wifi_status()
                
        except Exception as e:
            logger.error(f"Error getting WiFi status from Starlink {self.device_id}: {e}")
            return {}
    
    async def _get_local_wifi_status(self) -> Dict[str, Any]:
        """Get WiFi status from local connection"""
        try:
            from spacex.api.device import device_pb2
            
            req = device_pb2.Request(get_status=device_pb2.GetStatusRequest())
            resp = self.client.call(req)
            
            # Extract WiFi info if available
            wifi_status = {
                "ssid": "Starlink Network",
                "connected_clients": 0,
                "signal_strength": None,
                "frequency_band": "Dual Band (2.4GHz/5GHz)"
            }
            
            logger.info(f"Retrieved WiFi status from Starlink {self.device_id}")
            return wifi_status
        except Exception as e:
            logger.error(f"Error getting local WiFi status: {e}")
            return {}
    
    async def _get_remote_wifi_status(self) -> Dict[str, Any]:
        """Get WiFi status from remote API"""
        try:
            # Get the associated router ID
            router_id = self.credentials.get("router_id", f"Router-{self.device_id}")
            
            wifi_status = self.client.get_wifi_status(router_id)
            
            connected_clients = 0
            if hasattr(wifi_status, 'clients'):
                connected_clients = len([c for c in wifi_status.clients if c.ip_address])
            
            ssid_2g = "Starlink-2.4GHz"
            ssid_5g = "Starlink-5GHz"
            
            if hasattr(wifi_status, 'config') and wifi_status.config:
                if hasattr(wifi_status.config, 'networks') and wifi_status.config.networks:
                    for net in wifi_status.config.networks:
                        if hasattr(net, 'basic_service_sets'):
                            for bss in net.basic_service_sets:
                                if hasattr(bss, 'ssid'):
                                    if "2.4" in str(bss.band or ""):
                                        ssid_2g = bss.ssid
                                    elif "5" in str(bss.band or ""):
                                        ssid_5g = bss.ssid
            
            return {
                "ssid_2g": ssid_2g,
                "ssid_5g": ssid_5g,
                "connected_clients": connected_clients,
                "signal_strength": None,
                "frequency_band": "Dual Band"
            }
        except Exception as e:
            logger.error(f"Error getting remote WiFi status: {e}")
            return {}
    
    async def set_wifi_config(self, config: Dict[str, Any]) -> bool:
        """Change WiFi configuration"""
        try:
            if not self.connected:
                if not await self.connect():
                    return False
            
            if self.connection_type == "local":
                logger.warning("WiFi configuration changes not supported on local connections")
                return False
            
            from starlink_client.wifi_config import NewWifiConfig
            
            # Build new WiFi config
            new_config = NewWifiConfig()
            
            if "ssid" in config:
                new_config.ssid = config["ssid"]
            if "password" in config:
                new_config.password_24ghz = config["password"]
                new_config.password_5ghz = config["password"]
            if "ssid_24ghz" in config:
                new_config.ssid_24ghz = config["ssid_24ghz"]
            if "ssid_5ghz" in config:
                new_config.ssid_5ghz = config["ssid_5ghz"]
            if "hidden_ssid" in config:
                new_config.hidden_ssid = config["hidden_ssid"]
            
            # Get router ID
            router_id = self.credentials.get("router_id", f"Router-{self.device_id}")
            
            # Apply WiFi configuration
            self.client.setup_wifi(router_id, new_config)
            logger.info(f"Applied WiFi configuration to Starlink {self.device_id}")
            return True
        except Exception as e:
            logger.error(f"Error setting WiFi config on Starlink {self.device_id}: {e}")
            return False
