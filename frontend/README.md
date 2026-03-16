# Network Manager Frontend

Modern React dashboard for unified Starlink and MikroTik device management.

## ✨ Features

- 📊 **Real-time Dashboard**: Monitor all devices at a glance
- 🖥️ **Device Management**: Add, view, and control devices from a unified interface
- 📈 **Live Metrics**: CPU, memory, uptime, and traffic statistics
- ⚡ **Quick Actions**: Reboot, configure, and refresh devices with one click
- 🎨 **Modern UI**: Responsive dark theme with beautiful design
- 🔄 **Real-time Updates**: Auto-refresh metrics every 10 seconds
- 📱 **Fully Responsive**: Works on desktop, tablet, and mobile

## 🛠️ Technology Stack

- **React 18** - Modern UI framework
- **TypeScript** - Type-safe development
- **React Router v6** - Client-side routing
- **Axios** - HTTP client for API communication
- **Vite** - Lightning-fast build tool
- **CSS Modules** - Scoped, maintainable styling
- **Lucide React** - Beautiful icons

## 📦 Installation & Setup

### Prerequisites

- Node.js 16+ and npm (or yarn)

### Step 1: Install Dependencies

```bash
cd frontend
npm install
```

### Step 2: Start Development Server

```bash
npm run dev
```

The dashboard will be available at: **http://localhost:5173**

> The dev server automatically proxies API calls to `http://localhost:8000/api`

### Step 3: Build for Production

```bash
npm run build
```

Production-optimized build output goes to the `dist/` directory.

## 📁 Project Structure

```
frontend/
├── src/
│   ├── api.ts                    # API client & TypeScript types
│   ├── App.tsx                   # Root component with routing
│   ├── main.tsx                  # React entry point
│   ├── index.css                 # Global styles & CSS variables
│   ├── components/               # Reusable UI components
│   │   ├── Layout.tsx            # Main navigation & layout
│   │   ├── StatCard.tsx          # Statistics display cards
│   │   ├── DeviceCard.tsx        # Device information card
│   │   ├── AlertList.tsx         # Alert notifications
│   │   ├── Loading.tsx           # Loading spinner
│   │   └── *.module.css          # Component-scoped styles
│   │
│   └── pages/                    # Full page components
│       ├── Dashboard.tsx         # Main device overview
│       ├── DeviceDetail.tsx      # Device monitoring & control
│       ├── AddDevice.tsx         # Device registration form
│       └── *.module.css          # Page-scoped styles
│
├── index.html                    # HTML template
├── package.json
├── tsconfig.json                 # TypeScript configuration
├── vite.config.ts               # Vite build configuration
└── .gitignore
```

## 🎯 Key Pages

### 1. **Dashboard** (`/`)
Main landing page with:
- Quick statistics (total, online, offline devices)
- Device grid with status indicators
- Recent alerts panel
- Navigation to device details
- Quick link to add new devices

### 2. **Device Detail** (`/devices/:id`)
Comprehensive device monitoring:
- Real-time device information
- System metrics with visual graphs
- CPU/Memory usage percentages
- Uptime calculation
- Configuration display
- Action buttons:
  - **Refresh**: Update metrics from device
  - **Reboot**: Send reboot command to device

### 3. **Add Device** (`/add-device`)
Device registration form with:
- Device name
- Device type selector (Starlink/MikroTik)
- IP address
- Location label
- Optional credentials for MikroTik routers
- Form validation

## 🔌 API Integration

The frontend communicates with the FastAPI backend via REST API:

### Device Endpoints
```
GET    /api/devices/              # List all devices
GET    /api/devices/{id}          # Get device details
POST   /api/devices/              # Register new device
PUT    /api/devices/{id}          # Update device
DELETE /api/devices/{id}          # Remove device
```

### Control Endpoints
```
POST   /api/devices/{id}/refresh  # Get current status
POST   /api/devices/{id}/reboot   # Issue reboot command
GET    /api/devices/{id}/config   # Retrieve configuration
POST   /api/devices/{id}/config   # Apply configuration
```

### Dashboard Endpoints
```
GET    /api/dashboard/            # Aggregated statistics
GET    /api/dashboard/devices     # Device list with status
GET    /api/dashboard/alerts      # Recent alert notifications
GET    /api/dashboard/metrics/{id} # Historical metrics
```

## 🎨 Styling & Theme

### CSS Variables
The app uses a comprehensive set of CSS variables for easy theming:

```css
--primary: #3b82f6          /* Blue accent */
--primary-light: #60a5fa
--primary-dark: #1e40af

--success: #10b981          /* Green for online */
--warning: #f59e0b          /* Orange for warnings */
--error: #ef4444            /* Red for offline/errors */
--info: #06b6d4             /* Cyan for info */

--bg-dark: #0f172a          /* Main background */
--bg-darker: #020617
--bg-card: #1e293b          /* Card backgrounds */
--bg-hover: #334155         /* Hover state */

--text-primary: #e2e8f0     /* Main text */
--text-secondary: #cbd5e1
--text-tertiary: #94a3b8    /* Muted text */

--border: #334155           /* Borders */
```

### Component Styling
- All components use **CSS Modules** for scoped styling
- No global class naming conflicts
- Consistent spacing and typography
- Smooth transitions and animations
- Dark theme optimized for low-light viewing

## 🚀 Development

### Available Scripts

```bash
npm run dev          # Start development server
npm run build        # Create production build
npm run preview      # Preview production build locally
npm run lint         # Run ESLint
npm run type-check   # TypeScript type checking
```

### Code Style

- **TypeScript** strict mode enabled
- **ESLint** configured for React + TypeScript
- **CSS Modules** for all styling
- **Functional components** with React hooks

## 📊 Performance Features

- ✅ **Auto-refresh**: Metrics update every 10 seconds (configurable)
- ✅ **Async operations**: Non-blocking API calls
- ✅ **Code splitting**: Routes lazy-loaded by Vite
- ✅ **Optimized builds**: Minified production bundles
- ✅ **Efficient re-renders**: React 18 features

## 🔧 Troubleshooting

### Backend Connection Issues
```
Error: Failed to connect to API
```
**Solution:**
1. Verify backend is running: `python -m uvicorn app.main:app --reload`
2. Check backend URL in `vite.config.ts`
3. Ensure CORS is enabled in FastAPI:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],
       ...
   )
   ```

### Port Already in Use
```bash
# Use different port
npm run dev -- --port 5174
```

### Clear Cache & Reinstall
```bash
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Module Not Found
```bash
# Ensure all dependencies are installed
npm install
npm run type-check  # Verify types
```

## 📝 Environment Configuration

Create `.env.local` in the frontend directory if custom API endpoint is needed:

```
VITE_API_URL=http://localhost:8000/api
```

(Note: Development proxying is configured in `vite.config.ts`)

## 🤝 Contributing

Contributions are welcome! Please:

1. Follow existing code patterns
2. Use TypeScript for type safety
3. Keep components focused and reusable
4. Add CSS Modules for new styles
5. Test responsiveness on mobile

## 📄 License

MIT - See LICENSE file in project root

---

## Related Documentation

- [Backend Documentation](../backend/README.md)
- [Starlink Integration Guide](../backend/STARLINK_INTEGRATION.md)
- [API Documentation](../backend/README.md#api-endpoints)
- [Quick Start Guide](../QUICK_START.md)

### 2. Device Management
- Add/remove devices
- Device inventory with filters and search
- Device details view
- Real-time status and metrics

### 3. Device Control
- Remote reboot functionality
- Configuration management
- WiFi settings (for Starlink)
- Router settings (for MikroTik)

### 4. Monitoring
- Historical data and trends
- Performance reports
- Alert management
- Log viewer

### 5. User Management
- Role-based access control (RBAC)
- User authentication
- Activity logs

## Project Structure (TODO)

```
frontend/
├── public/
├── src/
│   ├── components/
│   │   ├── Dashboard/
│   │   ├── DeviceList/
│   │   ├── DeviceDetail/
│   │   └── Alerts/
│   ├── pages/
│   ├── services/
│   │   └── api.ts
│   ├── store/
│   ├── styles/
│   └── App.tsx
├── package.json
├── Dockerfile
└── nginx.conf
```

## Getting Started (Future)

This will be implemented after the backend is stable. The frontend will communicate with the backend API at `http://localhost:8000`.

## API Integration

The frontend will interact with these main API endpoints:

```
/api/devices          - Device management
/api/dashboard        - Dashboard data
/api/dashboard/alerts - Alert management
/api/auth            - Authentication (future)
```
