# Backend Setup Instructions

## Prerequisites

- Python 3.11+
- pip
- PostgreSQL (optional, SQLite used by default for development)

## Installation

### 1. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Create Environment File

```bash
# Copy example env file
cp .env.example .env

# Edit .env and configure as needed
```

### 4. Initialize Database

The database is automatically created on first run. For more advanced setup:

```bash
# If using Alembic migrations (future)
alembic upgrade head
```

## Running the Application

### Development

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

**Interactive API Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Production with Docker

```bash
docker-compose up --build
```

## API Endpoints

### Devices
- `GET /api/devices/` - List all devices
- `GET /api/devices/{device_id}` - Get device details
- `POST /api/devices/` - Add new device
- `PUT /api/devices/{device_id}` - Update device
- `DELETE /api/devices/{device_id}` - Delete device
- `POST /api/devices/{device_id}/reboot` - Reboot device
- `POST /api/devices/{device_id}/config` - Change device config
- `POST /api/devices/{device_id}/refresh` - Refresh device status

### Dashboard
- `GET /api/dashboard/` - Full dashboard data
- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /api/dashboard/alerts` - Get alerts
- `POST /api/dashboard/alerts/{alert_id}/resolve` - Resolve alert

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── devices.py       # Device endpoints
│   │   └── dashboard.py     # Dashboard endpoints
│   ├── modules/
│   │   ├── base.py          # Base driver interface
│   │   ├── starlink.py      # Starlink driver
│   │   └── mikrotik.py      # MikroTik driver
│   ├── models/
│   │   └── device.py        # Database models
│   ├── schemas/
│   │   └── device.py        # Pydantic schemas
│   ├── core/
│   │   ├── config.py        # Configuration
│   │   ├── database.py      # Database setup
│   │   └── security.py      # Authentication (future)
│   └── main.py              # FastAPI app
├── requirements.txt
├── Dockerfile
└── .env.example
```

## Configuration

### Database

- **Development**: SQLite (default, no setup needed)
- **Production**: PostgreSQL (configure `DATABASE_URL` in `.env`)

### Device Drivers

The system uses abstracted device drivers for Starlink and MikroTik:

- **Starlink**: Integrates with the starlink-client library
- **MikroTik**: Uses WinBox API via RouterOS

Both drivers implement the `BaseDeviceDriver` interface for a unified control interface.

## Next Steps

1. Implement actual Starlink and MikroTik client integrations
2. Add authentication and user management
3. Implement device monitoring background tasks
4. Build dashboard frontend (React/Vue)
5. Add test suite
6. Deploy to production
