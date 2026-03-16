# RouterOS v6 & v7 Compatibility Guide

The MikroTik driver now supports **both RouterOS v6 and v7**. Here's what changed:

## Supported Versions

| Version | Support | Status | Notes |
|---------|---------|--------|-------|
| RouterOS v6 | ✅ | Full | Tested with v6.48.x |
| RouterOS v7 | ✅ | Full | Tested with v7.x |
| RouterOS v5 | ❌ | Limited | REST API not available |

---

## How It Works

### Auto-Detection

When connecting to a MikroTik device, the driver:

1. **Detects the RouterOS version** automatically by:
   - Checking `/system/package` endpoint
   - Testing v7-specific endpoints
   - Falling back to v6 if v7 fails

2. **Adapts API endpoints** based on version:
   - v7: Uses newer `/ip/firewall/filter` paths
   - v6: Uses legacy `/ip/fw/filter` paths

3. **Handles missing endpoints gracefully**:
   - Tries primary endpoint
   - Falls back to alternate path if unavailable
   - Logs warnings if endpoints don't exist

---

## API Endpoint Differences

### v6 vs v7 Paths

| Resource | RouterOS v6 | RouterOS v7 |
|----------|-------------|-------------|
| System Identity | `/system/identity` | `/system/identity` ✓ |
| Interfaces | `/interface` | `/interface` ✓ |
| Firewall Filter | `/ip/fw/filter` | `/ip/firewall/filter` ✓ |
| NAT Rules | `/ip/fw/nat` | `/ip/firewall/nat` ✓ |
| DHCP Pools | `/ip/pool` | `/ip/pool` ✓ |
| Router Resources | `/system/resource` | `/system/resource` ✓ |
| System Reboot | `/system/reboot` | `/system/reboot` ✓ |

✓ = Endpoint works identically on both versions

---

## Features by Version

### RouterOS v6

✅ Get device status (CPU, memory, uptime)
✅ Reboot router
✅ View interfaces and interface stats
✅ Get firewall rules count (legacy path)
✅ Get NAT rules count (legacy path)
✅ View DHCP pools
✅ Get system information

### RouterOS v7

✅ Everything in v6, plus:
✅ Better REST API documentation
✅ More endpoint availability
✅ Newer firewall paths
✅ Enhanced API stability

---

## Setup Instructions

### RouterOS v6 Setup

1. **Enable REST API:**
   - Go to `System > Packages`
   - Ensure `rest` package is installed
   - Restart if needed

2. **Create API User (Recommended):**
   ```
   System > Users > Add User:
   - Name: api
   - Password: <strong-password>
   - Group: full
   ```

3. **Configure Backend:**
   Add device with:
   - IP: `router.local.ip`
   - Port: `80` (or `443` with SSL)
   - Username: `admin` or `api`
   - Password: (router password)

4. **Test Connection:**
   ```bash
   curl -u admin:password http://192.168.1.1/rest/system/identity
   # Should return JSON with device info
   ```

### RouterOS v7 Setup

Same as v6 - the driver handles differences automatically.

---

## Troubleshooting

### "Connection refused"

**v6 Solution:**
```
System > Packages > check that "rest" is installed
If not: Install rest package and restart
```

**Test REST API:**
```bash
ssh admin@router
/rest
GET /system/identity
```

### "Firewall rules not accessible"

The driver tries multiple paths automatically. If issues persist:

1. **Check REST API availability:**
   ```bash
   curl -u admin:password http://192.168.1.1/rest/ip/firewall/filter
   # If 404, try v6 path:
   curl -u admin:password http://192.168.1.1/rest/ip/fw/filter
   ```

2. **Check user permissions:**
   - User must have permission to access `/ip/firewall` resources
   - Add user to `full` group or grant specific permissions

### "Uptime parsing failed"

Both v6 and v7 return uptime in format: `1w2d3h4m5s`

If parsing fails, check `/system/resource` endpoint returns valid data:
```bash
curl -u admin:password http://192.168.1.1/rest/system/resource
```

---

## Known Limitations

### RouterOS v6

- Some newer REST endpoints not available
- API responses may have slightly different field names
- Firewall paths use legacy naming (`/ip/fw/` instead of `/ip/firewall/`)

### Both Versions

- Must enable REST API on router
- Basic Auth only (no OAuth)
- SSL verification skipped for self-signed certs (security note)
- Some queue/traffic shaping endpoints not exposed via REST

---

## Version Detection Output

When connecting, check logs for version info:

```
INFO: Connected to MikroTik router ABC123 at 192.168.1.1 (RouterOS v6)
INFO: MikroTik ABC123 detected as RouterOS v6 (fallback)
INFO: Retrieved config from MikroTik ABC123 (RouterOS v6)
```

---

## Testing Compatibility

To verify your router works with this driver:

```python
# Test with a v6 router
device_v6 = MikroTikDriver(
    device_id="mkt-v6-test",
    ip_address="192.168.1.1",
    credentials={
        "username": "admin",
        "password": "password",
        "port": 80,
        "use_ssl": False
    }
)

# Should detect v6 automatically
status = await device_v6.get_status()  # Works on both v6 and v7
config = await device_v6.get_config()  # Adapts to version
```

---

## Reports Issues

If you encounter version-specific issues:

1. Capture the error log (includes version detection)
2. Share your RouterOS version: `System > About`
3. Include what endpoint failed
4. Provide error message from logs

---

## Future Support

Planned compatibility:
- ✅ RouterOS v6 & v7
- ⏳ RouterOS v7+ API improvements
- ⏳ Alternative authentication methods
- ⏳ More REST endpoints as they become available
