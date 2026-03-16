# WireGuard VPN Setup Guide - Multi-Location Device Management

This guide sets up a secure VPN tunnel so your Render backend can reach devices in different locations (you + your brother in Yemen).

## Architecture

```
Yemen Setup (Brother)
├─ Local Starlink: 192.168.1.100
├─ WireGuard Client: 10.0.0.2
└─ Connected to VPN

     [WireGuard Tunnel]

Render Backend
├─ Running on: onrender.com
├─ WireGuard Server: 10.0.0.1:51820
└─ Can reach: 10.0.0.2 (Yemen)
     └─ Which can reach: 192.168.1.x (Yemen local network)

Frontend
└─ Uses same backend for both locations
```

---

## Step 1: Generate WireGuard Keys

Run this on your local machine:

```bash
# Install WireGuard (if not already installed)
# Windows: Download from https://www.wireguard.com/install/
# Linux: sudo apt-get install wireguard wireguard-tools
# macOS: brew install wireguard-tools

# Generate server keys
wg genkey | tee server_private.key | wg pubkey > server_public.key

# Generate client key (Yemen)
wg genkey | tee client_yemen_private.key | wg pubkey > client_yemen_public.key

# Show the keys
cat server_private.key
cat server_public.key
cat client_yemen_private.key
cat client_yemen_public.key
```

**Save these keys securely - you'll need them next!**

---

## Step 2: Configure Render Backend

### 2a. Add Environment Variables

Go to your Render dashboard → Your Service → Settings → Environment Variables

Add:
```
WIREGUARD_PRIVATE_KEY=<paste server_private.key content>
WIREGUARD_PUBLIC_KEY=<paste server_public.key content>
RENDER_SERVICE_ID=<your-service-id>
```

### 2b. Update Render Service

Render should auto-install WireGuard from the `.render/build.sh` script. If not, add to build.sh:

```bash
apt-get update
apt-get install -y wireguard wireguard-tools
```

### 2c. Redeploy

In Render Dashboard: Click **"Redeploy"**

---

## Step 3: Configure Yemen Client

### Give this file to your brother:

**File: `wireguard-yemen.conf`**

```
[Interface]
Address = 10.0.0.2/24
PrivateKey = <client_yemen_private.key>
DNS = 8.8.8.8, 8.8.4.4

[Peer]
PublicKey = <server_public.key>
Endpoint = <your-render-domain>.onrender.com:51820
AllowedIPs = 10.0.0.0/24
PersistentKeepalive = 25
```

Replace:
- `<client_yemen_private.key>` with the client private key from Step 1
- `<server_public.key>` with the server public key from Step 1
- `<your-render-domain>` with your actual Render domain (e.g., `starlink-manager-api.onrender.com`)

### Your brother's setup:

1. **Install WireGuard:**
   - Windows: https://www.wireguard.com/install/
   - Linux: `sudo apt-get install wireguard wireguard-tools`
   - macOS: `brew install wireguard-tools`

2. **Import the config:**
   - Open WireGuard
   - Click "Add Tunnel"
   - Select the `wireguard-yemen.conf` file
   - Click "Activate"

3. **Verify connection:**
   ```bash
   ping 10.0.0.1  # Should ping the Render backend
   ```

---

## Step 4: Update Backend Device Access

Now your backend can reach Yemen devices!

Instead of connecting to `192.168.1.100`, you need a mapping system.

### Option A: Update Device Model with Location

Edit `backend/app/models/device.py`:

```python
from enum import Enum

class DeviceLocation(str, Enum):
    LOCAL = "local"          # Your devices
    YEMEN = "yemen"          # Yemen devices
    SAUDI = "saudi"          # Future: other locations

class Device(Base):
    __tablename__ = "devices"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, index=True)
    location_type = Column(String, default=DeviceLocation.LOCAL)  # NEW
    ip_address = Column(String, unique=True, index=True)
    vpn_ip = Column(String, nullable=True)  # VPN tunnel IP if remote
```

### Option B: Update Device Connection Logic

Edit `backend/app/modules/base.py`:

```python
class BaseDeviceDriver:
    def __init__(self, device_id: str, ip_address: str, location: str = "local"):
        self.device_id = device_id
        self.location = location
        
        # Use VPN IP if it's a remote location
        if location == "yemen":
            self.ip_address = "10.0.0.2"  # Connect through VPN
        else:
            self.ip_address = ip_address  # Direct local connection
        
        self.connected = False
```

### Option C: Route Traffic Through VPN

When adding a Yemen device:
- IP Address in form: `192.168.1.100` (for reference)
- Backend automatically uses: `10.0.0.2` to reach it through VPN
- Since 10.0.0.2 can access Yemen's 192.168.1.x, it works!

---

## Step 5: Test the Setup

### Test 1: Verify VPN Tunnel

```bash
# On Yemen PC (with WireGuard active)
ping 10.0.0.1

# Should respond, proving tunnel is open
```

### Test 2: Add Yemen Device

1. Open your dashboard
2. Click "Add Device"
3. Fill in:
   - Name: "Yemen Starlink"
   - Type: "Starlink"
   - IP: `192.168.1.100` (Yemen local IP)
   - Location: "Yemen"
4. Submit

### Test 3: View Dashboard

The dashboard should show the Yemen device as online/offline based on actual connection status.

---

## Adding More Locations

To add more locations (e.g., Saudi Arabia):

1. **Generate keys:**
   ```bash
   wg genkey | tee client_saudi_private.key | wg pubkey > client_saudi_public.key
   ```

2. **Create config file:** `wireguard-saudi.conf`
   ```
   [Interface]
   Address = 10.0.0.3/24    # Note: different IP
   PrivateKey = <client_saudi_private.key>
   ...
   ```

3. **Update Render environment:** Add keys for Saudi setup

4. **Users import config and connect**

---

## Troubleshooting

### "Connection refused" on backend
- Verify WireGuard is running: `wg show` (on Render backend)
- Check port 51820 is open
- Verify keys match in client config

### "Cannot reach devices"
- Verify VPN is connected: `ping 10.0.0.1`
- Check firewall on Yemen router allows backend to reach local devices
- Verify device IP is correct (192.168.1.x, not 10.0.0.x)

### "VPN drops after 5 minutes"
- Add to client config: `PersistentKeepalive = 25`
- Increases stability on unstable connections

---

## Security Notes

✅ All traffic encrypted end-to-end
✅ Keys rotate per location
✅ Only authorized peers can connect
⚠️ Keep private keys secret!
⚠️ Don't share config files with others

---

## Cost

- **Render:** Free tier supports this
- **Bandwidth:** VPN tunnel counts toward Render's bandwidth limits
- **Additional:** $0

---

## Next Steps

1. Generate keys (Step 1)
2. Configure Render (Step 2)
3. Send config to brother (Step 3)
4. Update backend code (Step 4)
5. Test connection (Step 5)
6. Start adding Yemen devices!

**Questions?** Check the main README or WireGuard docs.
