"""
MikroTik Device Driver

Integrates with the MikroTik RestAPI to manage RouterOS devices.
Supports querying interface stats, managing firewall, retrieving system info, etc.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
import logging
import httpx
import base64
from app.modules.base import BaseDeviceDriver, DeviceInfo

logger = logging.getLogger(__name__)


class MikroTikDriver(BaseDeviceDriver):
    """Driver for managing MikroTik routers via REST API"""
    
    def __init__(self, device_id: str, ip_address: str, credentials: Dict[str, Any]):
        super().__init__(device_id, ip_address, credentials)
        self.client: Optional[httpx.AsyncClient] = None
        self.username = credentials.get("username", "admin")
        self.password = credentials.get("password", "")
        self.port = credentials.get("port", 80)
        self.use_ssl = credentials.get("use_ssl", False)
        self.timeout = 10
        self.os_version = None  # Will be detected on connect
        
        
    def _get_base_url(self) -> str:
        """Build base URL for RouterOS REST API"""
        protocol = "https" if self.use_ssl else "http"
        return f"{protocol}://{self.ip_address}:{self.port}/rest"
    
    def _get_auth_header(self) -> Dict[str, str]:
        """Generate HTTP Basic Auth header"""
        credentials = f"{self.username}:{self.password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return {"Authorization": f"Basic {encoded}"}
    
    async def _detect_version(self) -> str:
        """Detect RouterOS version (v6 or v7+)"""
        if self.os_version:
            return self.os_version
        
        try:
            url = f"{self._get_base_url()}/system/package"
            response = await self.client.get(url, headers=self._get_auth_header())
            
            if response.status_code == 200:
                packages = response.json()
                for pkg in packages:
                    if pkg.get("name") == "system":
                        version_str = pkg.get("version", "6.0")
                        major_version = int(version_str.split(".")[0])
                        self.os_version = f"v{major_version}"
                        logger.info(f"MikroTik {self.device_id} detected as RouterOS {self.os_version}")
                        return self.os_version
            
            # Fallback: test v7 API, if fails assume v6
            test_url = f"{self._get_base_url()}/interface/ethernet"
            test_response = await self.client.get(test_url, headers=self._get_auth_header())
            
            if test_response.status_code == 200:
                self.os_version = "v7"
            else:
                self.os_version = "v6"
                
            logger.info(f"MikroTik {self.device_id} detected as RouterOS {self.os_version} (fallback)")
            return self.os_version
        except Exception as e:
            logger.warning(f"Could not detect MikroTik version, assuming v6: {e}")
            self.os_version = "v6"
            return self.os_version
    
    async def connect(self) -> bool:
        """
        Establish connection to MikroTik router via REST API
        
        Tests connectivity by retrieving system identity.
        Automatically detects RouterOS version (v6 or v7+).
        """
        try:
            self.client = httpx.AsyncClient(
                verify=not self.use_ssl,  # Skip SSL verification for self-signed certs
                timeout=self.timeout
            )
            
            # Test connection by getting system identity (works on both v6 and v7)
            url = f"{self._get_base_url()}/system/identity"
            response = await self.client.get(url, headers=self._get_auth_header())
            
            if response.status_code == 200:
                # Detect version
                await self._detect_version()
                logger.info(f"Connected to MikroTik router {self.device_id} at {self.ip_address} (RouterOS {self.os_version})")
                self.connected = True
                return True
            else:
                logger.error(f"Failed to authenticate with MikroTik {self.device_id}: {response.status_code}")
                self.connected = False
                return False
                
        except Exception as e:
            logger.error(f"Failed to connect to MikroTik {self.device_id}: {e}")
            self.connected = False
            return False
    
    async def disconnect(self) -> bool:
        """Close connection to device"""
        try:
            if self.client:
                await self.client.aclose()
            self.connected = False
            logger.info(f"Disconnected from MikroTik {self.device_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to disconnect from MikroTik {self.device_id}: {e}")
            return False
    
    async def get_status(self) -> DeviceInfo:
        """Get MikroTik router status and metrics"""
        try:
            if not self.connected:
                await self.connect()
            
            # Get system resource info
            url = f"{self._get_base_url()}/system/resource"
            response = await self.client.get(url, headers=self._get_auth_header())
            
            resource_data = response.json()[0] if response.status_code == 200 else {}
            
            # Get system identity
            identity_url = f"{self._get_base_url()}/system/identity"
            identity_response = await self.client.get(identity_url, headers=self._get_auth_header())
            identity_data = identity_response.json()[0] if identity_response.status_code == 200 else {}
            
            router_name = identity_data.get("name", f"MikroTik-{self.device_id[-4:]}")
            cpu_load = float(resource_data.get("cpu-load", 0))
            memory_used = float(resource_data.get("total-memory", 0))
            memory_free = float(resource_data.get("free-memory", 0))
            memory_usage = (memory_used - memory_free) / memory_used * 100 if memory_used > 0 else 0
            
            # Parse uptime (format: "1w2d3h4m5s")
            uptime_str = resource_data.get("uptime", "0s")
            uptime_seconds = self._parse_uptime(uptime_str)
            
            device_info = DeviceInfo(
                id=self.device_id,
                name=router_name,
                status="online",
                ip_address=self.ip_address,
                cpu_usage=cpu_load,
                memory_usage=memory_usage,
                uptime=uptime_seconds,
                last_updated=datetime.utcnow()
            )
            logger.info(f"MikroTik {self.device_id} status: CPU={cpu_load}%, Memory={memory_usage:.1f}%")
            return device_info
        except Exception as e:
            logger.error(f"Error getting status from MikroTik {self.device_id}: {e}")
            return DeviceInfo(
                id=self.device_id,
                name=f"MikroTik-{self.device_id[-4:]}",
                status="error",
                ip_address=self.ip_address,
                last_updated=datetime.utcnow()
            )
    
    async def reboot(self) -> bool:
        """Reboot the MikroTik router"""
        try:
            if not self.connected:
                await self.connect()
            
            url = f"{self._get_base_url()}/system/reboot"
            response = await self.client.post(url, headers=self._get_auth_header())
            
            if response.status_code in [200, 204]:
                logger.info(f"Issued reboot command to MikroTik {self.device_id}")
                return True
            else:
                logger.error(f"Failed to reboot MikroTik {self.device_id}: HTTP {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Failed to reboot MikroTik {self.device_id}: {e}")
            return False
    
    async def get_config(self) -> Dict[str, Any]:
        """Get MikroTik configuration (system identity, interfaces, etc.)"""
        try:
            if not self.connected:
                await self.connect()
            
            # Get system identity (works on both v6 and v7)
            identity_url = f"{self._get_base_url()}/system/identity"
            identity_response = await self.client.get(identity_url, headers=self._get_auth_header())
            identity = identity_response.json()[0] if identity_response.status_code == 200 else {}
            
            # Get interfaces (works on both v6 and v7)
            interface_url = f"{self._get_base_url()}/interface"
            interface_response = await self.client.get(interface_url, headers=self._get_auth_header())
            interfaces = interface_response.json() if interface_response.status_code == 200 else []
            
            # Get firewall filter rules (may differ between v6 and v7)
            firewall_rules = 0
            try:
                # Try v7 path first
                filter_url = f"{self._get_base_url()}/ip/firewall/filter"
                filter_response = await self.client.get(filter_url, headers=self._get_auth_header())
                if filter_response.status_code == 200:
                    firewall_rules = len(filter_response.json())
                else:
                    # Fallback for v6
                    filter_url_v6 = f"{self._get_base_url()}/ip/fw/filter"
                    filter_response_v6 = await self.client.get(filter_url_v6, headers=self._get_auth_header())
                    firewall_rules = len(filter_response_v6.json()) if filter_response_v6.status_code == 200 else 0
            except Exception as e:
                logger.warning(f"Could not retrieve firewall rules for {self.device_id}: {e}")
            
            # Get NAT rules (may differ between v6 and v7)
            nat_rules = 0
            try:
                # Try v7 path first
                nat_url = f"{self._get_base_url()}/ip/firewall/nat"
                nat_response = await self.client.get(nat_url, headers=self._get_auth_header())
                if nat_response.status_code == 200:
                    nat_rules = len(nat_response.json())
                else:
                    # Fallback for v6
                    nat_url_v6 = f"{self._get_base_url()}/ip/fw/nat"
                    nat_response_v6 = await self.client.get(nat_url_v6, headers=self._get_auth_header())
                    nat_rules = len(nat_response_v6.json()) if nat_response_v6.status_code == 200 else 0
            except Exception as e:
                logger.warning(f"Could not retrieve NAT rules for {self.device_id}: {e}")
            
            # Get DHCP pools (works on both)
            dhcp_pools = 0
            try:
                dhcp_url = f"{self._get_base_url()}/ip/pool"
                dhcp_response = await self.client.get(dhcp_url, headers=self._get_auth_header())
                dhcp_pools = len(dhcp_response.json()) if dhcp_response.status_code == 200 else 0
            except Exception as e:
                logger.warning(f"Could not retrieve DHCP pools for {self.device_id}: {e}")
            
            config = {
                "identity": identity.get("name", "Unknown"),
                "interfaces": [{"name": i.get("name"), "disabled": i.get("disabled", False)} for i in interfaces],
                "firewall_rules": firewall_rules,
                "nat_rules": nat_rules,
                "dhcp_pools": dhcp_pools,
                "system": {
                    "architecture": identity.get("architecture-name", ""),
                    "platform": identity.get("platform", ""),
                    "version": self.os_version
                }
            }
            logger.info(f"Retrieved config from MikroTik {self.device_id} (RouterOS {self.os_version})")
            return config
        except Exception as e:
            logger.error(f"Error getting config from MikroTik {self.device_id}: {e}")
            return {}
    
    async def set_config(self, config: Dict[str, Any]) -> bool:
        """Apply configuration changes to MikroTik system"""
        try:
            if not self.connected:
                await self.connect()
            
            # Update system identity
            if "identity" in config:
                url = f"{self._get_base_url()}/system/identity"
                payload = {"name": config["identity"]}
                response = await self.client.patch(url, json=payload, headers=self._get_auth_header())
                if response.status_code not in [200, 204]:
                    logger.error(f"Failed to update identity: {response.status_code}")
                    return False
            
            # Enable/disable interfaces
            if "interfaces" in config:
                for interface in config["interfaces"]:
                    if "name" in interface:
                        # Get interface ID
                        list_url = f"{self._get_base_url()}/interface?name={interface['name']}"
                        list_response = await self.client.get(list_url, headers=self._get_auth_header())
                        if list_response.status_code == 200:
                            interfaces = list_response.json()
                            if interfaces:
                                iface_id = interfaces[0].get(".id")
                                update_url = f"{self._get_base_url()}/interface/{iface_id}"
                                payload = {"disabled": interface.get("disabled", False)}
                                await self.client.patch(update_url, json=payload, headers=self._get_auth_header())
            
            logger.info(f"Applied configuration changes to MikroTik {self.device_id}")
            return True
        except Exception as e:
            logger.error(f"Error setting config on MikroTik {self.device_id}: {e}")
            return False
    
    async def get_interface_stats(self) -> Dict[str, Any]:
        """Get detailed interface statistics including traffic"""
        try:
            if not self.connected:
                await self.connect()
            
            # Get interface statistics
            url = f"{self._get_base_url()}/interface"
            response = await self.client.get(url, headers=self._get_auth_header())
            
            interfaces = []
            total_in = 0
            total_out = 0
            
            if response.status_code == 200:
                for iface in response.json():
                    bytes_in = int(iface.get("rx-byte", 0))
                    bytes_out = int(iface.get("tx-byte", 0))
                    packets_in = int(iface.get("rx-packet", 0))
                    packets_out = int(iface.get("tx-packet", 0))
                    
                    interfaces.append({
                        "name": iface.get("name"),
                        "disabled": iface.get("disabled", False),
                        "running": iface.get("running", False),
                        "mtu": iface.get("mtu", 0),
                        "rx_bytes": bytes_in,
                        "tx_bytes": bytes_out,
                        "rx_packets": packets_in,
                        "tx_packets": packets_out
                    })
                    total_in += bytes_in
                    total_out += bytes_out
            
            stats = {
                "interfaces": interfaces,
                "total_traffic_in": total_in,
                "total_traffic_out": total_out,
                "active_interfaces": sum(1 for i in interfaces if i.get("running", False))
            }
            logger.info(f"Retrieved interface stats from MikroTik {self.device_id}")
            return stats
        except Exception as e:
            logger.error(f"Error getting interface stats from MikroTik {self.device_id}: {e}")
            return {}
    
    async def get_firewall_rules(self) -> Dict[str, Any]:
        """Get firewall rules and connection statistics"""
        try:
            if not self.connected:
                await self.connect()
            
            # Get NAT rules
            nat_url = f"{self._get_base_url()}/ip/firewall/nat"
            nat_response = await self.client.get(nat_url, headers=self._get_auth_header())
            nat_rules = nat_response.json() if nat_response.status_code == 200 else []
            
            # Get filter rules
            filter_url = f"{self._get_base_url()}/ip/firewall/filter"
            filter_response = await self.client.get(filter_url, headers=self._get_auth_header())
            filter_rules = filter_response.json() if filter_response.status_code == 200 else []
            
            # Get mangle rules
            mangle_url = f"{self._get_base_url()}/ip/firewall/mangle"
            mangle_response = await self.client.get(mangle_url, headers=self._get_auth_header())
            mangle_rules = mangle_response.json() if mangle_response.status_code == 200 else []
            
            # Get connection tracking stats
            conn_url = f"{self._get_base_url()}/ip/firewall/connection/tracking"
            conn_response = await self.client.get(conn_url, headers=self._get_auth_header())
            conn_tracking = conn_response.json()[0] if conn_response.status_code == 200 else {}
            
            rules = {
                "nat_rules": [
                    {
                        "chain": r.get("chain"),
                        "action": r.get("action"),
                        "src-address": r.get("src-address"),
                        "dst-address": r.get("dst-address"),
                        "protocol": r.get("protocol"),
                        "disabled": r.get("disabled", False)
                    }
                    for r in nat_rules
                ],
                "filter_rules": len(filter_rules),
                "mangle_rules": len(mangle_rules),
                "connection_count": int(conn_tracking.get("count", 0)),
                "connection_limit": int(conn_tracking.get("limit", 0))
            }
            logger.info(f"Retrieved firewall rules from MikroTik {self.device_id}")
            return rules
        except Exception as e:
            logger.error(f"Error getting firewall rules from MikroTik {self.device_id}: {e}")
            return {}
    
    def _parse_uptime(self, uptime_str: str) -> int:
        """Parse MikroTik uptime string format (e.g., '1w2d3h4m5s') to seconds"""
        total_seconds = 0
        import re
        
        patterns = {
            'w': 604800,  # weeks
            'd': 86400,   # days
            'h': 3600,    # hours
            'm': 60,      # minutes
            's': 1        # seconds
        }
        
        for unit, seconds in patterns.items():
            match = re.search(rf'(\d+){unit}', uptime_str)
            if match:
                total_seconds += int(match.group(1)) * seconds
        
        return total_seconds
    
    async def enable_bandwidth_limit(self, interface: str, limit_mbps: float) -> bool:
        """Enable bandwidth limiting on an interface"""
        try:
            if not self.connected:
                await self.connect()
            
            # TODO: Configure actual bandwidth limit
            # This typically involves queue configuration
            
            return True
        except Exception as e:
            print(f"Error setting bandwidth limit on MikroTik {self.device_id}: {e}")
            return False
