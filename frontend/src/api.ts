import axios from 'axios';

const API_BASE_URL = '/api';

export interface Device {
  id: string;
  name: string;
  device_type: 'starlink' | 'mikrotik';
  ip_address: string;
  location: string;
  description?: string;
  status: 'online' | 'offline' | 'error' | 'unknown';
  last_latency?: number;
  last_download_speed?: number;
  last_upload_speed?: number;
  cpu_usage?: number;
  memory_usage?: number;
  uptime?: number;
  created_at: string;
  updated_at: string;
  last_seen?: string;
  last_online?: string;
}

export interface DeviceStatus {
  id: string;
  name: string;
  status: string;
  ip_address: string;
  cpu_usage?: number;
  memory_usage?: number;
  uptime?: number;
  last_updated: string;
}

export interface DashboardStats {
  total_devices: number;
  online_devices: number;
  offline_devices: number;
  error_devices?: number;
  starlink_count?: number;
  mikrotik_count?: number;
  avg_latency?: number;
  avg_download_speed?: number;
}

export interface DashboardResponse {
  stats: DashboardStats;
  devices: Device[];
  recent_alerts: Alert[];
}

export interface Metric {
  timestamp: string;
  value: number;
  device_id: string;
  metric_type: string;
}

export interface Alert {
  id: string;
  device_id: string;
  message: string;
  severity: 'info' | 'warning' | 'error' | 'critical';
  created_at: string;
  resolved: boolean;
}

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// Device APIs
export const deviceApi = {
  list: () => api.get<Device[]>('/devices/'),
  get: (id: string) => api.get<Device>(`/devices/${id}`),
  create: (device: Partial<Device>) => api.post<Device>('/devices/', device),
  update: (id: string, device: Partial<Device>) => api.put<Device>(`/devices/${id}`, device),
  delete: (id: string) => api.delete(`/devices/${id}`),
  refresh: (id: string) => api.post<DeviceStatus>(`/devices/${id}/refresh`),
  reboot: (id: string) => api.post(`/devices/${id}/reboot`),
  getConfig: (id: string) => api.get(`/devices/${id}/config`),
  setConfig: (id: string, config: any) => api.post(`/devices/${id}/config`, { config }),
};

// Dashboard APIs
export const dashboardApi = {
  getDashboard: () => api.get<DashboardResponse>('/dashboard/'),
  getStats: () => api.get<DashboardStats>('/dashboard/stats'),
  getMetrics: (deviceId: string, metricType?: string) =>
    api.get<Metric[]>(`/dashboard/metrics/${deviceId}`, { params: { metric_type: metricType } }),
};

// Health check
export const healthApi = {
  check: () => api.get('/'),
};

export default api;
