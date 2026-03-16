"""
WireGuard VPN Manager for multi-location device access

Allows the backend to reach devices at different locations through secure VPN tunnel.
Each location (e.g., Yemen, Saudi Arabia) connects via WireGuard to access their local devices.
"""

import subprocess
import logging
import os
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)

WIREGUARD_CONFIG_DIR = "/etc/wireguard"
WIREGUARD_INTERFACE = "wg0"


class WireGuardManager:
    """Manages WireGuard VPN for multi-location device access"""
    
    def __init__(self, interface: str = WIREGUARD_INTERFACE):
        self.interface = interface
        self.config_dir = Path(WIREGUARD_CONFIG_DIR)
        self.enabled = self._check_wireguard_available()
    
    def _check_wireguard_available(self) -> bool:
        """Check if WireGuard is installed"""
        try:
            subprocess.run(["wg", "version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("WireGuard not installed - VPN features disabled")
            return False
    
    def get_server_keys(self) -> dict:
        """Get server WireGuard keys from environment or generate"""
        private_key = os.environ.get("WIREGUARD_PRIVATE_KEY")
        public_key = os.environ.get("WIREGUARD_PUBLIC_KEY")
        
        if not private_key or not public_key:
            logger.error("WireGuard keys not configured. Set WIREGUARD_PRIVATE_KEY and WIREGUARD_PUBLIC_KEY")
            return {}
        
        return {
            "private_key": private_key,
            "public_key": public_key,
        }
    
    def add_peer(
        self,
        peer_name: str,
        peer_public_key: str,
        peer_ip: str = "10.0.0.2/32",
        description: str = ""
    ) -> bool:
        """
        Add a new peer (location) to the VPN
        
        Args:
            peer_name: Name of the location (e.g., "yemen", "saudi")
            peer_public_key: Public key of the peer
            peer_ip: IP address to assign (default 10.0.0.2 for first, then increment)
            description: Description of the location
        
        Returns:
            True if successful
        """
        if not self.enabled:
            logger.warning(f"WireGuard not available - cannot add peer {peer_name}")
            return False
        
        try:
            cmd = [
                "wg",
                "set",
                self.interface,
                "peer",
                peer_public_key,
                "allowed-ips",
                peer_ip,
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Added WireGuard peer: {peer_name} ({peer_ip})")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to add peer {peer_name}: {e}")
            return False
    
    def remove_peer(self, peer_public_key: str) -> bool:
        """Remove a peer from the VPN"""
        if not self.enabled:
            return False
        
        try:
            subprocess.run(
                ["wg", "set", self.interface, "peer", peer_public_key, "remove"],
                check=True,
                capture_output=True
            )
            logger.info(f"Removed WireGuard peer")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to remove peer: {e}")
            return False
    
    def get_peers(self) -> list:
        """Get list of all connected peers"""
        if not self.enabled:
            return []
        
        try:
            result = subprocess.run(
                ["wg", "show", self.interface],
                capture_output=True,
                text=True,
                check=True
            )
            # Parse output to extract peers
            peers = []
            for line in result.stdout.split('\n'):
                if line.startswith('peer:'):
                    peers.append(line.split('peer:')[1].strip())
            return peers
        except subprocess.CalledProcessError:
            return []
    
    def generate_client_config(
        self,
        client_name: str,
        client_public_key: str,
        client_private_key: str,
        server_endpoint: str,
        server_public_key: str,
        client_allowed_ips: str = "10.0.0.0/24",
        client_ip: str = "10.0.0.2/24"
    ) -> str:
        """
        Generate WireGuard client configuration file
        
        Args:
            client_name: Name of the client location
            client_private_key: Client's private key
            server_endpoint: Server endpoint (domain:port or ip:port)
            server_public_key: Server's public key
            client_allowed_ips: IP range client can access through VPN
            client_ip: Client's VPN IP address
        
        Returns:
            WireGuard configuration as string
        """
        config = f"""# WireGuard Configuration for {client_name}
# Generated for {client_name} device management

[Interface]
Address = {client_ip}
PrivateKey = {client_private_key}
DNS = 8.8.8.8, 8.8.4.4

[Peer]
PublicKey = {server_public_key}
Endpoint = {server_endpoint}
AllowedIPs = {client_allowed_ips}
PersistentKeepalive = 25
"""
        return config


# Initialize global manager
wireguard_manager = WireGuardManager()
