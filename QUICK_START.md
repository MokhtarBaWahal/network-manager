# Quick Start Guide - Network Manager Backend

## Status: ✅ Running and Tested

The FastAPI backend is now running and all endpoints are functional!

## Access the API

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Test the API
Run the test suite:
```bash
python test_api.py
```

## API Endpoints

### Health & Status
- `GET /` - Root endpoint with API info
- `GET /health` - Health check

### Device Management
- `GET /api/devices/` - List all devices
- `POST /api/devices/` - Create new device
- `GET /api/devices/{id}` - Get device details
- `PUT /api/devices/{id}` - Update device
- `DELETE /api/devices/{id}` - Delete device
- `POST /api/devices/{id}/reboot` - Reboot device
- `POST /api/devices/{id}/config` - Change configuration
- `POST /api/devices/{id}/refresh` - Refresh status

### Dashboard
- `GET /api/dashboard/` - Full dashboard data
- `GET /api/dashboard/stats` - Statistics summary
- `GET /api/dashboard/alerts` - List alerts
- `POST /api/dashboard/alerts/{id}/resolve` - Resolve alert

## Example: Create a Device

```bash
curl -X POST "http://localhost:8000/api/devices/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Main Starlink Dish",
    "device_type": "starlink",
    "ip_address": "192.168.1.100",
    "location": "New York",
    "description": "Primary internet connection"
  }'
```

## Example: Get Dashboard Stats

```bash
curl "http://localhost:8000/api/dashboard/stats" | python -m json.tool
```

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry
│   ├── api/
│   │   ├── devices.py       # Device endpoints
│   │   └── dashboard.py     # Dashboard endpoints
│   ├── modules/
│   │   ├── base.py          # Base device driver
│   │   ├── starlink.py      # Starlink implementation
│   │   └── mikrotik.py      # MikroTik implementation
│   ├── models/
│   │   └── device.py        # Database models
│   ├── schemas/
│   │   └── device.py        # Request/response schemas
│   └── core/
│       ├── config.py        # Configuration
│       └── database.py      # Database setup
├── requirements.txt         # Dependencies
├── Dockerfile               # Container configuration
├── .env.example             # Environment template
├── test_api.py              # Test suite
└── README.md                # Documentation
```

## Database

The database is automatically created on first run:
- **Location**: `./network_manager.db` (SQLite)
- **Tables**: devices, credentials, device_metrics, alerts

## Next Steps

1. **Integrate Starlink**: Update `app/modules/starlink.py` with actual client calls
2. **Integrate MikroTik**: Update `app/modules/mikrotik.py` with WinBox API
3. **Build Frontend**: Create React/Vue dashboard
4. **Add Authentication**: Implement JWT and user management

## Troubleshooting

### Port Already in Use
If port 8000 is in use:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### Database Issues
To reset the database:
```bash
rm network_manager.db
```

Then restart the server to recreate it clean.

## Configuration

Edit `.env` file to change settings:
```
DATABASE_URL=sqlite:///./network_manager.db
SECRET_KEY=your-secret-key
STARLINK_REFRESH_INTERVAL=30
MIKROTIK_REFRESH_INTERVAL=30
```

---

**Happy developing!** 🚀
