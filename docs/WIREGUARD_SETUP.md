# WireGuard Configuration for Multi-Location Device Management

## Setup Steps

### 1. On Your Render Backend

Edit `.render/build.sh`:

```bash
#!/bin/bash
set -e

echo "Installing WireGuard..."
apt-get update
apt-get install -y wireguard wireguard-tools

# Generate keys if not present
mkdir -p /etc/wireguard
if [ ! -f /etc/wireguard/server_private.key ]; then
  umask 077
  wg genkey | tee /etc/wireguard/server_private.key | wg pubkey > /etc/wireguard/server_public.key
fi

cd backend
pip install --upgrade pip
pip install -r requirements.txt
echo "Build complete!"
```

### 2. Update Backend with WireGuard Support

Install wireguard-python in requirements.txt:
```
wireguard-tools==0.0.1
```

### 3. Create WireGuard Configuration

File: `backend/app/core/wireguard.py`:

```python
import subprocess
import os
from pathlib import Path

class WireGuardManager:
    def __init__(self):
        self.config_dir = Path("/etc/wireguard")
        self.interface = "wg0"
    
    def setup(self):
        """Initialize WireGuard interface"""
        # This runs once on backend startup
        pass
    
    def add_peer(self, peer_name: str, peer_public_key: str, allowed_ips: str = "10.0.0.0/24"):
        """Add a new peer (e.g., Yemen location)"""
        cmd = f"wg set {self.interface} peer {peer_public_key} allowed-ips {allowed_ips}"
        subprocess.run(cmd, shell=True, check=True)
```

### 4. Configuration Files

**File: `/etc/wireguard/wg0.conf` (on Render)**
```
[Interface]
Address = 10.0.0.1/24
ListenPort = 51820
PrivateKey = <SERVER_PRIVATE_KEY>

[Peer]  # Yemen Location
PublicKey = <CLIENT_PUBLIC_KEY>
AllowedIPs = 10.0.0.2/32
```

**File: `wireguard-client.conf` (for your brother in Yemen)**
```
[Interface]
Address = 10.0.0.2/24
PrivateKey = <CLIENT_PRIVATE_KEY>
DNS = 8.8.8.8

[Peer]
PublicKey = <SERVER_PUBLIC_KEY>
Endpoint = your-render-app.onrender.com:51820
AllowedIPs = 10.0.0.0/24
PersistentKeepalive = 25
```

### 5. Expose VPN Port on Render

In your Render Dashboard:
1. Go to your service
2. **Settings** → **Environment** → Add:
   ```
   PORT=51820
   ```

### 6. Your Brother Sets Up Client

He needs to:
1. Install WireGuard: https://www.wireguard.com/install/
2. Import the `wireguard-client.conf` file
3. Enable the connection
4. Now his local network (192.168.x.x) is accessible to your backend via VPN tunnel

### 7. Access Devices Through VPN

From your backend, instead of:
```python
device_ip = "192.168.1.100"  # Won't work from cloud
```

Use the VPN tunnel:
```python
device_ip = "10.0.0.2"  # His Yemen location through VPN
```

---

## Benefits

✅ Secure end-to-end encryption
✅ Works from anywhere (cloud backend reaches remote devices)
✅ No port forwarding needed
✅ Easy to add more locations (just create more peers)
✅ ~$0 additional cost

## Testing

```bash
# On Render backend
ping 10.0.0.2  # Should reach Yemen setup

# On Yemen PC (after connecting to WireGuard)
ping 10.0.0.1  # Should reach Render backend
```

Both should work if VPN is properly configured.
