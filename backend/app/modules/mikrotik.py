"""
MikroTik Device Driver

Supports RouterOS v6 via binary API (routeros-api library, port 8728)
and RouterOS v7+ via REST API (HTTP/HTTPS).

In "auto" mode the driver tries binary first, then falls back to REST.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
import functools
import logging
import httpx
import base64
from concurrent.futures import ThreadPoolExecutor

from app.modules.base import BaseDeviceDriver, DeviceInfo

logger = logging.getLogger(__name__)

_binary_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="mikrotik_binary")


class _BinaryBackend:
    """Wraps synchronous routeros_api calls. All methods are sync-only."""

    def __init__(self, ip, port, username, password):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self._pool = None
        self._api = None

    def _sync_connect(self):
        import routeros_api
        self._pool = routeros_api.RouterOsApiPool(
            self.ip,
            username=self.username,
            password=self.password,
            port=self.port,
            plaintext_login=True,
        )
        self._api = self._pool.get_api()
        self._api.get_resource('/system/identity').get()  # verify connection

    def _sync_disconnect(self):
        if self._pool:
            try:
                self._pool.disconnect()
            except Exception:
                pass

    def _sync_get_identity(self) -> dict:
        return self._api.get_resource('/system/identity').get()[0]

    def _sync_get_resource(self) -> dict:
        return self._api.get_resource('/system/resource').get()[0]

    def _sync_get_interfaces(self) -> list:
        return self._api.get_resource('/interface').get()

    def _sync_reboot(self):
        self._api.get_resource('/system/reboot').call()

    def _sync_get_firewall_filter(self) -> list:
        return self._api.get_resource('/ip/firewall/filter').get()

    def _sync_get_firewall_nat(self) -> list:
        return self._api.get_resource('/ip/firewall/nat').get()

    def _sync_get_firewall_mangle(self) -> list:
        return self._api.get_resource('/ip/firewall/mangle').get()

    def _sync_get_ip_pool(self) -> list:
        return self._api.get_resource('/ip/pool').get()

    def _sync_set_identity(self, name: str):
        self._api.get_resource('/system/identity').set(name=name)

    def _sync_set_interface_disabled(self, iface_name: str, disabled: bool):
        r = self._api.get_resource('/interface')
        items = r.get(name=iface_name)
        if items:
            r.set(id=items[0]['.id'], disabled=('yes' if disabled else 'no'))

    def _sync_get_dhcp_leases(self) -> list:
        return self._api.get_resource('/ip/dhcp-server/lease').get()

    def _sync_get_hotspot_active(self) -> list:
        return self._api.get_resource('/ip/hotspot/active').get()

    def _sync_get_health(self) -> list:
        return self._api.get_resource('/system/health').get()


class MikroTikDriver(BaseDeviceDriver):
    """Driver for managing MikroTik routers via binary API (v6) or REST API (v7+)"""

    def __init__(self, device_id: str, ip_address: str, credentials: Dict[str, Any]):
        super().__init__(device_id, ip_address, credentials)
        self.client: Optional[httpx.AsyncClient] = None
        self.username = credentials.get("username", "admin")
        self.password = credentials.get("password", "")
        self.use_ssl = credentials.get("use_ssl", False)
        self.timeout = 5
        self.os_version = None

        self.api_type = credentials.get("api_type", "auto")  # "binary" | "rest" | "auto"
        _user_port = credentials.get("port", None)
        self._binary_port = _user_port if _user_port else 8728
        self._rest_port = _user_port if _user_port else (443 if self.use_ssl else 80)

        self._active_api: Optional[str] = None   # "binary" or "rest"
        self._binary_backend: Optional[_BinaryBackend] = None
        self._binary_lock = asyncio.Lock()
        self._connect_lock = asyncio.Lock()

    # ------------------------------------------------------------------
    # Async executor helpers
    # ------------------------------------------------------------------

    async def _run_binary(self, fn, *args):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_binary_executor, fn, *args)

    async def _run_binary_kw(self, fn, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_binary_executor, functools.partial(fn, **kwargs))

    # ------------------------------------------------------------------
    # REST helpers
    # ------------------------------------------------------------------

    def _get_base_url(self) -> str:
        protocol = "https" if self.use_ssl else "http"
        return f"{protocol}://{self.ip_address}:{self._rest_port}/rest"

    def _get_auth_header(self) -> Dict[str, str]:
        creds = f"{self.username}:{self.password}"
        encoded = base64.b64encode(creds.encode()).decode()
        return {"Authorization": f"Basic {encoded}"}

    # ------------------------------------------------------------------
    # connect / disconnect
    # ------------------------------------------------------------------

    async def connect(self) -> bool:
        async with self._connect_lock:
            # Re-check after acquiring lock — another coroutine may have connected while we waited
            if self.connected:
                return True

            logger.info(f"Connecting to MikroTik {self.device_id} at {self.ip_address} (api_type={self.api_type})")

            # Try binary API
            if self.api_type in ("binary", "auto"):
                try:
                    backend = _BinaryBackend(
                        self.ip_address, self._binary_port, self.username, self.password
                    )
                    await self._run_binary(backend._sync_connect)
                    self._binary_backend = backend
                    self._active_api = "binary"
                    self.connected = True
                    logger.info(f"Connected to MikroTik {self.device_id} via binary API (port {self._binary_port})")
                    return True
                except Exception as e:
                    logger.warning(f"Binary API connection failed for {self.device_id}: {e}")
                    if self.api_type == "binary":
                        self.connected = False
                        return False
                    # fall through to REST

            # Try REST API
            try:
                logger.info(f"   Trying REST API at {self._get_base_url()}")
                self.client = httpx.AsyncClient(
                    verify=not self.use_ssl,
                    timeout=self.timeout,
                )
                url = f"{self._get_base_url()}/system/identity"
                response = await self.client.get(url, headers=self._get_auth_header())
                if response.status_code == 200:
                    self._active_api = "rest"
                    self.connected = True
                    logger.info(f"OK Connected to MikroTik {self.device_id} via REST API (port {self._rest_port})")
                    return True
                else:
                    logger.error(f"ERROR REST auth failed for {self.device_id}: HTTP {response.status_code}")
                    self.connected = False
                    return False
            except Exception as e:
                logger.error(f"ERROR REST connection failed for {self.device_id}: {e}")
                self.connected = False
                return False

    async def disconnect(self) -> bool:
        try:
            if self._active_api == "binary" and self._binary_backend:
                await self._run_binary(self._binary_backend._sync_disconnect)
            if self.client:
                await self.client.aclose()
                self.client = None
            self.connected = False
            logger.info(f"Disconnected from MikroTik {self.device_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to disconnect from MikroTik {self.device_id}: {e}")
            return False

    # ------------------------------------------------------------------
    # Error helper
    # ------------------------------------------------------------------

    def _error_device_info(self) -> DeviceInfo:
        return DeviceInfo(
            id=self.device_id,
            name=f"MikroTik-{self.device_id[-4:]}",
            status="error",
            ip_address=self.ip_address,
            last_updated=datetime.utcnow(),
        )

    # ------------------------------------------------------------------
    # get_status
    # ------------------------------------------------------------------

    async def get_status(self) -> DeviceInfo:
        logger.info(f">> Getting status for MikroTik {self.device_id}...")
        try:
            if not self.connected:
                await self.connect()
            if not self.connected:
                return self._error_device_info()

            if self._active_api == "binary":
                return await self._get_status_binary()
            return await self._get_status_rest()
        except Exception as e:
            logger.error(f"ERROR Error getting status from MikroTik {self.device_id}: {e}", exc_info=True)
            return self._error_device_info()

    async def _get_status_binary(self) -> DeviceInfo:
        async with self._binary_lock:
            resource = await self._run_binary(self._binary_backend._sync_get_resource)
            identity = await self._run_binary(self._binary_backend._sync_get_identity)

        cpu_load = float(resource.get("cpu-load", 0))
        total_mem = float(resource.get("total-memory", 0))
        free_mem = float(resource.get("free-memory", 0))
        memory_usage = (total_mem - free_mem) / total_mem * 100 if total_mem > 0 else 0
        uptime_seconds = self._parse_uptime(resource.get("uptime", "0s"))
        router_name = identity.get("name", f"MikroTik-{self.device_id[-4:]}")

        logger.info(f"OK MikroTik {self.device_id} [binary] CPU={cpu_load}%, Mem={memory_usage:.1f}%, Uptime={uptime_seconds}s")
        return DeviceInfo(
            id=self.device_id,
            name=router_name,
            status="online",
            ip_address=self.ip_address,
            cpu_usage=cpu_load,
            memory_usage=memory_usage,
            uptime=uptime_seconds,
            last_updated=datetime.utcnow(),
        )

    async def _get_status_rest(self) -> DeviceInfo:
        resource_url = f"{self._get_base_url()}/system/resource"
        resource_response = await self.client.get(resource_url, headers=self._get_auth_header())
        resource_data = resource_response.json()[0] if resource_response.status_code == 200 else {}

        identity_url = f"{self._get_base_url()}/system/identity"
        identity_response = await self.client.get(identity_url, headers=self._get_auth_header())
        identity_data = identity_response.json()[0] if identity_response.status_code == 200 else {}

        router_name = identity_data.get("name", f"MikroTik-{self.device_id[-4:]}")
        cpu_load = float(resource_data.get("cpu-load", 0))
        memory_used = float(resource_data.get("total-memory", 0))
        memory_free = float(resource_data.get("free-memory", 0))
        memory_usage = (memory_used - memory_free) / memory_used * 100 if memory_used > 0 else 0
        uptime_seconds = self._parse_uptime(resource_data.get("uptime", "0s"))

        logger.info(f"OK MikroTik {self.device_id} [rest] CPU={cpu_load}%, Mem={memory_usage:.1f}%, Uptime={uptime_seconds}s")
        return DeviceInfo(
            id=self.device_id,
            name=router_name,
            status="online",
            ip_address=self.ip_address,
            cpu_usage=cpu_load,
            memory_usage=memory_usage,
            uptime=uptime_seconds,
            last_updated=datetime.utcnow(),
        )

    # ------------------------------------------------------------------
    # reboot
    # ------------------------------------------------------------------

    async def reboot(self) -> bool:
        try:
            if not self.connected:
                await self.connect()
            if self._active_api == "binary":
                return await self._reboot_binary()
            return await self._reboot_rest()
        except Exception as e:
            logger.error(f"Failed to reboot MikroTik {self.device_id}: {e}")
            return False

    async def _reboot_binary(self) -> bool:
        async with self._binary_lock:
            try:
                await self._run_binary(self._binary_backend._sync_reboot)
                return True
            except Exception as e:
                # Router drops connection immediately after reboot — expected
                if any(k in type(e).__name__ for k in ["Connection", "EOF", "Disconnect"]):
                    return True
                raise

    async def _reboot_rest(self) -> bool:
        url = f"{self._get_base_url()}/system/reboot"
        response = await self.client.post(url, headers=self._get_auth_header())
        if response.status_code in [200, 204]:
            logger.info(f"Issued reboot command to MikroTik {self.device_id}")
            return True
        logger.error(f"Failed to reboot MikroTik {self.device_id}: HTTP {response.status_code}")
        return False

    # ------------------------------------------------------------------
    # get_config
    # ------------------------------------------------------------------

    async def get_config(self) -> Dict[str, Any]:
        try:
            if not self.connected:
                await self.connect()
            if self._active_api == "binary":
                return await self._get_config_binary()
            return await self._get_config_rest()
        except Exception as e:
            logger.error(f"Error getting config from MikroTik {self.device_id}: {e}")
            return {}

    async def _get_config_binary(self) -> Dict[str, Any]:
        async with self._binary_lock:
            identity = await self._run_binary(self._binary_backend._sync_get_identity)
            interfaces_raw = await self._run_binary(self._binary_backend._sync_get_interfaces)
            try:
                filter_rules = await self._run_binary(self._binary_backend._sync_get_firewall_filter)
            except Exception:
                filter_rules = []
            try:
                nat_rules = await self._run_binary(self._binary_backend._sync_get_firewall_nat)
            except Exception:
                nat_rules = []
            try:
                pools = await self._run_binary(self._binary_backend._sync_get_ip_pool)
            except Exception:
                pools = []

        return {
            "identity": identity.get("name", "Unknown"),
            "interfaces": [{"name": i.get("name"), "disabled": i.get("disabled", "false")} for i in interfaces_raw],
            "firewall_rules": len(filter_rules),
            "nat_rules": len(nat_rules),
            "dhcp_pools": len(pools),
            "system": {"version": "v6"},
        }

    async def _get_config_rest(self) -> Dict[str, Any]:
        identity_url = f"{self._get_base_url()}/system/identity"
        identity_response = await self.client.get(identity_url, headers=self._get_auth_header())
        identity = identity_response.json()[0] if identity_response.status_code == 200 else {}

        interface_url = f"{self._get_base_url()}/interface"
        interface_response = await self.client.get(interface_url, headers=self._get_auth_header())
        interfaces = interface_response.json() if interface_response.status_code == 200 else []

        firewall_rules = 0
        try:
            filter_url = f"{self._get_base_url()}/ip/firewall/filter"
            filter_response = await self.client.get(filter_url, headers=self._get_auth_header())
            if filter_response.status_code == 200:
                firewall_rules = len(filter_response.json())
        except Exception as e:
            logger.warning(f"Could not retrieve firewall rules for {self.device_id}: {e}")

        nat_rules = 0
        try:
            nat_url = f"{self._get_base_url()}/ip/firewall/nat"
            nat_response = await self.client.get(nat_url, headers=self._get_auth_header())
            if nat_response.status_code == 200:
                nat_rules = len(nat_response.json())
        except Exception as e:
            logger.warning(f"Could not retrieve NAT rules for {self.device_id}: {e}")

        dhcp_pools = 0
        try:
            dhcp_url = f"{self._get_base_url()}/ip/pool"
            dhcp_response = await self.client.get(dhcp_url, headers=self._get_auth_header())
            dhcp_pools = len(dhcp_response.json()) if dhcp_response.status_code == 200 else 0
        except Exception as e:
            logger.warning(f"Could not retrieve DHCP pools for {self.device_id}: {e}")

        return {
            "identity": identity.get("name", "Unknown"),
            "interfaces": [{"name": i.get("name"), "disabled": i.get("disabled", False)} for i in interfaces],
            "firewall_rules": firewall_rules,
            "nat_rules": nat_rules,
            "dhcp_pools": dhcp_pools,
            "system": {
                "architecture": identity.get("architecture-name", ""),
                "platform": identity.get("platform", ""),
                "version": self.os_version,
            },
        }

    # ------------------------------------------------------------------
    # set_config
    # ------------------------------------------------------------------

    async def set_config(self, config: Dict[str, Any]) -> bool:
        try:
            if not self.connected:
                await self.connect()
            if self._active_api == "binary":
                return await self._set_config_binary(config)
            return await self._set_config_rest(config)
        except Exception as e:
            logger.error(f"Error setting config on MikroTik {self.device_id}: {e}")
            return False

    async def _set_config_binary(self, config: Dict[str, Any]) -> bool:
        async with self._binary_lock:
            if "identity" in config:
                await self._run_binary_kw(
                    self._binary_backend._sync_set_identity, name=config["identity"]
                )
            if "interfaces" in config:
                for iface in config["interfaces"]:
                    if "name" in iface:
                        disabled = iface.get("disabled", False)
                        await self._run_binary_kw(
                            self._binary_backend._sync_set_interface_disabled,
                            iface_name=iface["name"],
                            disabled=disabled,
                        )
        logger.info(f"Applied configuration changes to MikroTik {self.device_id} [binary]")
        return True

    async def _set_config_rest(self, config: Dict[str, Any]) -> bool:
        if "identity" in config:
            url = f"{self._get_base_url()}/system/identity"
            payload = {"name": config["identity"]}
            response = await self.client.patch(url, json=payload, headers=self._get_auth_header())
            if response.status_code not in [200, 204]:
                logger.error(f"Failed to update identity: {response.status_code}")
                return False

        if "interfaces" in config:
            for interface in config["interfaces"]:
                if "name" in interface:
                    list_url = f"{self._get_base_url()}/interface?name={interface['name']}"
                    list_response = await self.client.get(list_url, headers=self._get_auth_header())
                    if list_response.status_code == 200:
                        ifaces = list_response.json()
                        if ifaces:
                            iface_id = ifaces[0].get(".id")
                            update_url = f"{self._get_base_url()}/interface/{iface_id}"
                            payload = {"disabled": interface.get("disabled", False)}
                            await self.client.patch(update_url, json=payload, headers=self._get_auth_header())

        logger.info(f"Applied configuration changes to MikroTik {self.device_id} [rest]")
        return True

    # ------------------------------------------------------------------
    # get_interface_stats
    # ------------------------------------------------------------------

    async def get_interface_stats(self) -> Dict[str, Any]:
        try:
            if not self.connected:
                await self.connect()
            if self._active_api == "binary":
                return await self._get_interface_stats_binary()
            return await self._get_interface_stats_rest()
        except Exception as e:
            logger.error(f"Error getting interface stats from MikroTik {self.device_id}: {e}")
            return {}

    async def _get_interface_stats_binary(self) -> Dict[str, Any]:
        async with self._binary_lock:
            raw = await self._run_binary(self._binary_backend._sync_get_interfaces)
        return self._parse_interface_list(raw)

    async def _get_interface_stats_rest(self) -> Dict[str, Any]:
        url = f"{self._get_base_url()}/interface"
        response = await self.client.get(url, headers=self._get_auth_header())
        raw = response.json() if response.status_code == 200 else []
        return self._parse_interface_list(raw)

    def _parse_interface_list(self, raw: list) -> Dict[str, Any]:
        interfaces = []
        total_in = 0
        total_out = 0
        for iface in raw:
            if not isinstance(iface, dict):
                continue
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
                "tx_packets": packets_out,
            })
            total_in += bytes_in
            total_out += bytes_out
        logger.info(f"Retrieved interface stats from MikroTik {self.device_id}")
        return {
            "interfaces": interfaces,
            "total_traffic_in": total_in,
            "total_traffic_out": total_out,
            "active_interfaces": sum(1 for i in interfaces if i.get("running", False)),
        }

    # ------------------------------------------------------------------
    # get_firewall_rules
    # ------------------------------------------------------------------

    async def get_firewall_rules(self) -> Dict[str, Any]:
        try:
            if not self.connected:
                await self.connect()
            if self._active_api == "binary":
                return await self._get_firewall_rules_binary()
            return await self._get_firewall_rules_rest()
        except Exception as e:
            logger.error(f"Error getting firewall rules from MikroTik {self.device_id}: {e}")
            return {}

    async def _get_firewall_rules_binary(self) -> Dict[str, Any]:
        async with self._binary_lock:
            try:
                nat_rules = await self._run_binary(self._binary_backend._sync_get_firewall_nat)
            except Exception:
                nat_rules = []
            try:
                filter_rules = await self._run_binary(self._binary_backend._sync_get_firewall_filter)
            except Exception:
                filter_rules = []
            try:
                mangle_rules = await self._run_binary(self._binary_backend._sync_get_firewall_mangle)
            except Exception:
                mangle_rules = []

        return self._parse_firewall_data(nat_rules, filter_rules, mangle_rules, {})

    async def _get_firewall_rules_rest(self) -> Dict[str, Any]:
        nat_url = f"{self._get_base_url()}/ip/firewall/nat"
        nat_response = await self.client.get(nat_url, headers=self._get_auth_header())
        nat_rules = nat_response.json() if nat_response.status_code == 200 else []

        filter_url = f"{self._get_base_url()}/ip/firewall/filter"
        filter_response = await self.client.get(filter_url, headers=self._get_auth_header())
        filter_rules = filter_response.json() if filter_response.status_code == 200 else []

        mangle_url = f"{self._get_base_url()}/ip/firewall/mangle"
        mangle_response = await self.client.get(mangle_url, headers=self._get_auth_header())
        mangle_rules = mangle_response.json() if mangle_response.status_code == 200 else []

        conn_url = f"{self._get_base_url()}/ip/firewall/connection/tracking"
        conn_response = await self.client.get(conn_url, headers=self._get_auth_header())
        conn_tracking = conn_response.json()[0] if conn_response.status_code == 200 else {}

        return self._parse_firewall_data(nat_rules, filter_rules, mangle_rules, conn_tracking)

    def _parse_firewall_data(self, nat_rules, filter_rules, mangle_rules, conn_tracking) -> Dict[str, Any]:
        logger.info(f"Retrieved firewall rules from MikroTik {self.device_id}")
        return {
            "nat_rules": [
                {
                    "chain": r.get("chain"),
                    "action": r.get("action"),
                    "src-address": r.get("src-address"),
                    "dst-address": r.get("dst-address"),
                    "protocol": r.get("protocol"),
                    "disabled": r.get("disabled", False),
                }
                for r in nat_rules
            ],
            "filter_rules": len(filter_rules),
            "mangle_rules": len(mangle_rules),
            "connection_count": int(conn_tracking.get("count", 0)),
            "connection_limit": int(conn_tracking.get("limit", 0)),
        }

    # ------------------------------------------------------------------
    # get_dhcp_leases
    # ------------------------------------------------------------------

    async def get_dhcp_leases(self) -> list:
        """Get DHCP lease list (connected devices)."""
        try:
            if not self.connected:
                await self.connect()
            if not self.connected:
                return []
            if self._active_api == "binary":
                async with self._binary_lock:
                    return await self._run_binary(self._binary_backend._sync_get_dhcp_leases)
            url = f"{self._get_base_url()}/ip/dhcp-server/lease"
            response = await self.client.get(url, headers=self._get_auth_header())
            return response.json() if response.status_code == 200 else []
        except Exception as e:
            logger.warning(f"Could not get DHCP leases from {self.device_id}: {e}")
            return []

    # ------------------------------------------------------------------
    # get_hotspot_active
    # ------------------------------------------------------------------

    async def get_hotspot_active(self) -> list:
        """Get active hotspot sessions (returns [] if hotspot not enabled)."""
        try:
            if not self.connected:
                await self.connect()
            if not self.connected:
                return []
            if self._active_api == "binary":
                async with self._binary_lock:
                    return await self._run_binary(self._binary_backend._sync_get_hotspot_active)
            url = f"{self._get_base_url()}/ip/hotspot/active"
            response = await self.client.get(url, headers=self._get_auth_header())
            return response.json() if response.status_code == 200 else []
        except Exception as e:
            logger.warning(f"Could not get hotspot active from {self.device_id}: {e}")
            return []

    # ------------------------------------------------------------------
    # get_health
    # ------------------------------------------------------------------

    async def get_health(self) -> dict:
        """Get hardware health sensors (voltage, temperature, fans). Returns {} if unsupported."""
        try:
            if not self.connected:
                await self.connect()
            if not self.connected:
                return {}
            def _health_list_to_dict(items: list) -> dict:
                result = {}
                for i, item in enumerate(items):
                    key = item.get("name") or item.get("type") or f"sensor_{i}"
                    value = item.get("value", "")
                    if key and value != "":
                        result[key] = value
                return result

            if self._active_api == "binary":
                async with self._binary_lock:
                    raw = await self._run_binary(self._binary_backend._sync_get_health)
                if isinstance(raw, list):
                    return _health_list_to_dict(raw)
                return raw if isinstance(raw, dict) else {}
            url = f"{self._get_base_url()}/system/health"
            response = await self.client.get(url, headers=self._get_auth_header())
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    return _health_list_to_dict(data)
                return data if isinstance(data, dict) else {}
            return {}
        except Exception as e:
            logger.warning(f"Could not get health from {self.device_id}: {e}")
            return {}

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def _parse_uptime(self, uptime_str: str) -> int:
        """Parse MikroTik uptime string (e.g. '1w2d3h4m5s') to seconds"""
        import re
        total_seconds = 0
        patterns = {'w': 604800, 'd': 86400, 'h': 3600, 'm': 60, 's': 1}
        for unit, seconds in patterns.items():
            match = re.search(rf'(\d+){unit}', uptime_str)
            if match:
                total_seconds += int(match.group(1)) * seconds
        return total_seconds

    async def enable_bandwidth_limit(self, interface: str, limit_mbps: float) -> bool:
        """Enable bandwidth limiting on an interface (stub)"""
        try:
            if not self.connected:
                await self.connect()
            # TODO: Configure queue-based bandwidth limiting
            return True
        except Exception as e:
            logger.error(f"Error setting bandwidth limit on MikroTik {self.device_id}: {e}")
            return False
