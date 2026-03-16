# Test VPN Setup - Step by Step Guide

This guide walks you through testing the WireGuard + Multi-Location device management setup with your brother before rolling out to other clients.

---

## **Access the Test Page**

1. **Open the dashboard:** `https://network-manager-alpha.vercel.app/` (or your local dev server)
2. **Click "🧪 Test VPN Setup"** button in the top right of the Dashboard
3. You'll see the test page with demo configuration and test tools

---

## **Phase 1: Local Connection Test** (Your Setup)

### **Setup:**
1. Make sure your Starlink or MikroTik router is on your local network
2. Know its IP address (e.g., `192.168.1.100`)

### **Test Steps:**
1. Go to `/test-vpn`
2. Select **"Local Direct"** (should be selected by default)
3. Enter your router's IP: `192.168.1.100`
4. Enter port: `80` or `443` (depends on your device)
5. Click **"Run All Tests"**

### **Expected Results:**
✅ Backend Connection: Success
✅ Device Discovery: Found devices
✅ Device Connection: Connected
✅ Local Network: Using direct local connection

### **Troubleshooting:**
- If "Device Connection" fails, verify:
  - Device IP is correct (can you ping it?)
  - Device is on same WiFi network
  - REST API is enabled on device

---

## **Phase 2: WireGuard VPN Setup**

### **Prerequisites:**
- Backend (Render) deployed and running
- WireGuard installed on your machine
- Brother has WireGuard ready to install

### **Generate Keys** (Do this once)

Open terminal and run:

```powershell
# Install cryptography if needed
pip install cryptography

# Generate keys
python -c "
from cryptography.hazmat.primitives.asymmetric import x25519
from base64 import b64encode

def generate_key():
    privkey = x25519.X25519PrivateKey.generate()
    return b64encode(privkey.private_bytes_raw()).decode()

def get_pubkey(privkey_b64):
    from base64 import b64decode
    privkey = x25519.X25519PrivateKey.from_private_bytes(b64decode(privkey_b64))
    return b64encode(privkey.public_key().public_bytes_raw()).decode()

srvpriv = generate_key()
srvpub = get_pubkey(srvpriv)
clipriv = generate_key()
clipub = get_pubkey(clipriv)

print(f'SERVER_PRIVATE_KEY={srvpriv}')
print(f'SERVER_PUBLIC_KEY={srvpub}')
print(f'CLIENT_PRIVATE_KEY={clipriv}')
print(f'CLIENT_PUBLIC_KEY={clipub}')
"
```

**Save all 4 keys in a file** - you'll need them.

### **Configure Render Backend**

1. Go to Render Dashboard → Your app → Settings
2. Add Environment Variables:
   ```
   WIREGUARD_PRIVATE_KEY=<paste SERVER_PRIVATE_KEY>
   WIREGUARD_PUBLIC_KEY=<paste SERVER_PUBLIC_KEY>
   ```
3. Click **"Redeploy"** - wait 2-3 minutes

### **Create Yemen Config File**

Create a file called `wireguard-yemen.conf`:

```
[Interface]
Address = 10.0.0.2/24
PrivateKey = <paste CLIENT_PRIVATE_KEY>
DNS = 8.8.8.8, 8.8.4.4

[Peer]
PublicKey = <paste SERVER_PUBLIC_KEY>
Endpoint = your-render-app.onrender.com:51820
AllowedIPs = 10.0.0.0/24
PersistentKeepalive = 25
```

**Send this file to your brother** (don't share keys in chat!)

### **Brother's Setup (Yemen)**

1. **Install WireGuard:**
   - Download from https://www.wireguard.com/install/
   - Open it

2. **Import config:**
   - Click "Add Tunnel"
   - Select the `wireguard-yemen.conf` file
   - Click "Activate"

3. **Verify connection:**
   ```bash
   ping 10.0.0.1  # Should work
   ```

---

## **Phase 3: Yemen Connection Test** (Through VPN)

### **Test Steps:**

1. **Make sure:**
   - Your backend is running/deployed
   - Brother's WireGuard tunnel is active
   - Yemen router is at `192.168.1.1` (or verify actual IP)

2. **Go to Test VPN page**
3. Select **"VPN Remote"**
4. Verify VPN IP shows: `10.0.0.2`
5. Click **"Test Device Connection"**

### **Expected Output:**

```
Manual Device Test: pending
Connected to MikroTik v6 - Brother at 10.0.0.2 successfully!
CPU: 15%, Memory: 62%, Uptime: 45 days
```

### **Troubleshooting:**

❌ **"Cannot reach device"**
- Check: Is WireGuard active on brother's PC?
  - Run: `wg show`
  - Should show active peer
  
- Check: Can you ping the VPN IP?
  - Run: `ping 10.0.0.2`
  
❌ **"VPN connection drops"**
- Add to Yemen config: `PersistentKeepalive = 25`
- May need to reconnect if internet unstable

---

## **Phase 4: Add Yemen Device in Dashboard**

Once tests pass, add the actual device:

1. **Open dashboard**
2. Click **"+ Add Device"**
3. Fill in:
   - **Name:** Yemen Starlink or Yemen MikroTik
   - **Device Type:** Starlink or MikroTik
   - **IP Address:** `192.168.1.1` (Yemen local IP)
   - **Location:** Yemen
4. Click **"Save"**

### **Expected Result:**

The device appears in the dashboard and shows:
- Status: Online (if responding) or Offline
- CPU, Memory, Uptime stats
- Can reboot, configure, etc.

---

## **Phase 5: Scale to More Clients**

Once everything works with your brother:

1. **Document your exact setup** - save all commands
2. **Create client setup guide** using the template:
   - Render backend URL
   - Device type (v6 or v7 MikroTik vs Starlink)
   - WireGuard instructions
   - Example configs

3. **Test with 1-2 more clients** before full rollout
4. **Adjust guide based on feedback**

---

## **Test Scenarios Matrix**

| Scenario | Location | Connection | Expected | Test Page |
|----------|----------|-----------|----------|-----------|
| Local test | Your home | Direct | ✅ Success | "Local Direct" |
| VPN initial | Yemen | Tunnel | ✅ Success | "VPN Remote" |
| Dashboard | Both | API | ✅ Devices show | Dashboard |
| Add device | Yemen | Via tunnel | ✅ Online status | Dashboard |

---

## **Common Issues & Solutions**

### Issue: "Backend Connection: Error"
**Solution:**
- Backend might be sleeping (Render free tier)
- Check if backend still running
- Try clicking "Run All Tests" again

### Issue: "Device Connection: Timeout"
**Solution:**
- Device IP might be wrong
- Try pinging the IP first
- Check firewall on router

### Issue: "VPN Tunnel: Not connecting"
**Solution:**
- Verify WireGuard keys match in config
- Check endpoint is correct
- Try: `wg show`

### Issue: "Can add device but still offline"
**Solution:**
- Device might be offline (power, network issue)
- Check device is reachable with ping
- Verify REST API enabled on device

---

## **What to Track During Test**

Keep notes on:

1. **Time to complete each phase** (useful for client docs)
2. **Which devices worked/failed** (RouterOS versions, Starlink models)
3. **Network issues encountered** (latency, drops, etc.)
4. **Questions from brother** (use for FAQ)

---

## **Next Steps After Successful Test**

1. ✅ Document what worked
2. ✅ Create client onboarding guide
3. ✅ Prepare WireGuard config template
4. ✅ Set up automated key generation (optional)
5. ✅ Ready for client rollout!

---

## **Need Help?**

Check:
- Backend logs: Render Dashboard → Logs
- Browser console: F12 → Console tab
- WireGuard status: `wg show` in terminal
- Ping test: `ping <device-ip>`

---

**Good luck! Let me know how the test goes! 🚀**
