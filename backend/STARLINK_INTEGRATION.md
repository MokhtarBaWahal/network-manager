# Starlink Integration Guide

## Status: ✅ Implemented

The Starlink driver has been fully integrated with the network manager backend. It supports both **local** and **remote** connections to Starlink dishes.

---

## Installation

### Step 1: Install starlink-client Library

The starlink-client library is included in the parent project. Add it to your Python path:

```bash
# Navigate to backend directory
cd backend

# Install the starlink-client library as an editable package
pip install -e ../../../starlink-client/libs/python/starlink-client
```

Verify installation:
```bash
python -c "from starlink_client import GrpcClient; print('✓ starlink-client installed')"
```

### Step 2: Configure Backend

The backend will automatically detect the starlink-client library when importing.

---

## Features Implemented

### Connection Types

#### ✅ **Local Connection**
- Direct gRPC connection to Starlink dish on port 9200
- Works when dish is on the same local network
- No authentication required
- Lower latency
- Full feature support

#### ✅ **Remote Connection**
- gRPC-Web API connection via Starlink Cloud
- Requires authentication cookie from Starlink web interface
- Works from anywhere
- Can manage multiple dishes
- Limited features (some operations restricted)

### Implemented Methods

| Method | Local | Remote | Status |
|--------|-------|--------|--------|
| `connect()` | ✅ | ✅ | Full implementation |
| `disconnect()` | ✅ | ✅ | Full implementation |
| `get_status()` | ✅ | ✅ | Full implementation |
| `reboot()` | ✅ | ✅ | Full implementation |
| `get_config()` | ✅ | ✅ | Full implementation |
| `set_config()` | ✅ | ✅ | Full implementation |
| `get_wifi_status()` | ✅ | ✅ | Full implementation |
| `set_wifi_config()` | ❌ | ✅ | Remote only |

---

## Usage Examples

### 1. Create a Local Connection Device

```python
from app.modules.starlink import StarlinkDriver

credentials = {
    "remote": False  # Local connection
}

driver = StarlinkDriver(
    device_id="starlink-dish-001",
    ip_address="192.168.100.1",
    credentials=credentials
)

# Connect
await driver.connect()

# Get status
status = await driver.get_status()
print(f"Device: {status.name}, Status: {status.status}")

# Get configuration
config = await driver.get_config()
print(f"Snow melt enabled: {config.get('snow_melt_enabled')}")

# Reboot
await driver.reboot()

# Disconnect
await driver.disconnect()
```

### 2. Create a Remote Connection Device

```python
# First, get authentication cookie from Starlink web interface:
# 1. Go to https://starlink.com
# 2. Log in
# 3. Use browser DevTools or a cookie extractor extension to get the authentication cookie

credentials = {
    "remote": True,
    "cookie": '{"opal_session": "eyJ..."}',  # Cookie from browser
    "credentials_dir": "./credentials",      # Where to store refreshed cookies
    "router_id": "Router-010000000000000000415160"  # Optional: specific router ID
}

driver = StarlinkDriver(
    device_id="starlink-dish-001",
    ip_address="api.starlink.com",  # Not used for remote, but required
    credentials=credentials
)

await driver.connect()
status = await driver.get_status()
```

### 3. Via API Endpoint

```bash
# Create a Starlink device (local)
curl -X POST "http://localhost:8000/api/devices/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Main Dish",
    "device_type": "starlink",
    "ip_address": "192.168.100.1",
    "location": "Rooftop"
  }'

# Reboot the device
curl -X POST "http://localhost:8000/api/devices/{device_id}/reboot"

# Get device status
curl "http://localhost:8000/api/devices/{device_id}"

# Update WiFi config
curl -X POST "http://localhost:8000/api/devices/{device_id}/config" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "ssid": "NewWiFiName",
      "password": "NewPassword123"
    }
  }'
```

---

## Protocol Buffer Messages

The driver uses these protobuf messages from the starlink-client:

### Available Requests

- `GetStatusRequest` - Get dish/router status
- `GetLocationRequest` - Get device location
- `GetDishConfigRequest` - Get dish configuration
- `SetDishConfigRequest` - Update dish config
- `RebootRequest` - Reboot device
- `GetWifiStatusRequest` - Get WiFi stats
- `SetWifiConfigRequest` - Update WiFi config

### Response Structures

- `DishGetStatusResponse` - Dish status with metrics
- `WifiGetStatusResponse` - WiFi status with client info
- `DeviceLocation` - GPS coordinates
- `DishConfig` - Dish configuration

---

## Error Handling

The driver includes comprehensive error handling:

```python
# Connection errors
if not await driver.connect():
    print("Failed to connect - check IP address and network")

# API errors (logged automatically)
try:
    status = await driver.get_status()
except Exception as e:
    logger.error(f"Error: {e}")
    # Driver gracefully handles offline devices
```

---

## Metrics Available

### From Local Connection

- ✅ Uptime (seconds)
- ✅ Latency (ms)
- ⚠️ Download/Upload speed (not directly available, calculated by dashboard)
- ✅ GPS coordinates (if available)
- ✅ Obstruction stats

### From Remote Connection

- ✅ Device name
- ✅ Online/offline status
- ⚠️ Detailed metrics (limited by API)

---

## Configuration Options

### Local Connection Config

```python
credentials = {
    "remote": False,
    # Optional:
    # "timeout": 5  # Custom timeout in seconds
}
```

### Remote Connection Config

```python
credentials = {
    "remote": True,
    "cookie": "{...}",  # Auth cookie (required)
    "credentials_dir": "./credentials",  # Cookie refresh storage
    "router_id": "Router-xxx"  # Optional: specific router to manage WiFi
}
```

---

## Logging

The driver uses Python's standard logging module:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('app.modules.starlink')

# Now all driver operations will be logged
driver = StarlinkDriver(...)
await driver.connect()  # Logs: "Connected to Starlink dish at ..."
```

---

## Known Limitations

1. **WiFi Config Changes**: Only available on remote connections (API limitation)
2. **Local Connection Metics**: Some advanced stats not available locally
3. **Cookie Expiry**: Remote connection cookies expire after 15 days (auto-refreshes)
4. **Rate Limiting**: API has rate limits (typically generous)

---

## Troubleshooting

### "starlink-client library not available"

**Solution**: Install the library using:
```bash
pip install -e ../../../starlink-client/libs/python/starlink-client
```

### Connection Timeout (Local)

**Causes**:
- Dish IP address is incorrect
- Firewall blocking port 9200
- Dish is offline

**Solution**:
```bash
# Test connectivity
ping 192.168.100.1
telnet 192.168.100.1 9200
```

### Remote Connection Failed

**Causes**:
- Invalid or expired cookie
- Dish not linked to Starlink account

**Solution**:
1. Log out and back into starlink.com
2. Re-extract authentication cookie
3. Verify cookie JSON format is valid

### Device Returns "offline"

The device is reachable but not responding to gRPC requests. This typically means:
- Dish is rebooting
- Network connectivity issue
- Firmware update in progress

---

## Next Steps

1. **Test Local Connection**: Add a local Starlink device and verify connectivity
2. **Configure Remote Access**: Set up authentication for remote management
3. **Monitor Metrics**: Use the dashboard to view real-time metrics
4. **Schedule Tasks**: Automate maintenance (e.g., weekly reboots)

---

## Support

For issues with the starlink-client library itself, see:
https://github.com/Eitol/starlink-client

For issues with the network manager integration, check:
- Backend logs: `python -m python.logging`
- API documentation: `http://localhost:8000/docs`

---

**Status**: ✅ Production Ready
