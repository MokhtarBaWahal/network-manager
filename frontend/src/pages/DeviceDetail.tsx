import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, RefreshCw, Power } from 'lucide-react';
import { deviceApi, Device, DeviceStatus } from '../api';
import Loading from '../components/Loading';
import styles from './DeviceDetail.module.css';

export default function DeviceDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [device, setDevice] = useState<Device | null>(null);
  const [status, setStatus] = useState<DeviceStatus | null>(null);
  const [config, setConfig] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    if (id) {
      fetchDevice();
      fetchStatus();
    }
  }, [id]);

  async function fetchDevice() {
    try {
      const res = await deviceApi.get(id!);
      setDevice(res.data);
    } catch (err) {
      setError('Failed to load device');
    }
  }

  async function fetchStatus() {
    try {
      const statusRes = await deviceApi.refresh(id!);
      setStatus(statusRes.data);

      const configRes = await deviceApi.getConfig(id!);
      setConfig(configRes.data);

      setLoading(false);
    } catch (err) {
      setError('Failed to load device status');
      setLoading(false);
    }
  }

  async function handleReboot() {
    setActionLoading(true);
    try {
      await deviceApi.reboot(id!);
      alert('Reboot command sent successfully');
      fetchStatus();
    } catch (err) {
      alert('Failed to send reboot command');
    } finally {
      setActionLoading(false);
    }
  }

  async function handleRefresh() {
    setActionLoading(true);
    try {
      await fetchStatus();
    } finally {
      setActionLoading(false);
    }
  }

  if (loading) return <Loading />;

  return (
    <div className={styles.detail}>
      <button className={styles.backButton} onClick={() => navigate('/')}>
        <ArrowLeft size={20} />
        Back
      </button>

      {error && <div className={styles.error}>{error}</div>}

      {device && status && (
        <>
          <div className={styles.header}>
            <h1>{device.name}</h1>
            <div className={styles.actions}>
              <button
                className={`${styles.btn} ${styles.secondary}`}
                onClick={handleRefresh}
                disabled={actionLoading}
              >
                <RefreshCw size={18} />
                Refresh
              </button>
              <button
                className={`${styles.btn} ${styles.danger}`}
                onClick={handleReboot}
                disabled={actionLoading}
              >
                <Power size={18} />
                Reboot
              </button>
            </div>
          </div>

          <div className={styles.grid}>
            {/* Device Information */}
            <div className={styles.card}>
              <h2>Device Information</h2>
              <div className={styles.info}>
                <div className={styles.infoRow}>
                  <span className={styles.label}>Device Type</span>
                  <span className={styles.value}>{device.device_type}</span>
                </div>
                <div className={styles.infoRow}>
                  <span className={styles.label}>IP Address</span>
                  <span className={styles.value}>{device.ip_address}</span>
                </div>
                <div className={styles.infoRow}>
                  <span className={styles.label}>Location</span>
                  <span className={styles.value}>{device.location || 'Not specified'}</span>
                </div>
                <div className={styles.infoRow}>
                  <span className={styles.label}>Status</span>
                  <span className={`${styles.value} ${styles[status.status]}`}>
                    {status.status}
                  </span>
                </div>
              </div>
            </div>

            {/* System Metrics */}
            <div className={styles.card}>
              <h2>System Metrics</h2>
              <div className={styles.metrics}>
                {status.cpu_usage !== undefined && (
                  <div className={styles.metric}>
                    <div className={styles.metricLabel}>CPU Usage</div>
                    <div className={styles.metricValue}>{status.cpu_usage?.toFixed(1)}%</div>
                    <div className={styles.metricBar}>
                      <div
                        className={styles.metricFill}
                        style={{ width: `${status.cpu_usage}%` }}
                      ></div>
                    </div>
                  </div>
                )}
                {status.memory_usage !== undefined && (
                  <div className={styles.metric}>
                    <div className={styles.metricLabel}>Memory Usage</div>
                    <div className={styles.metricValue}>{status.memory_usage?.toFixed(1)}%</div>
                    <div className={styles.metricBar}>
                      <div
                        className={styles.metricFill}
                        style={{ width: `${status.memory_usage}%` }}
                      ></div>
                    </div>
                  </div>
                )}
                {status.uptime !== undefined && (
                  <div className={styles.metric}>
                    <div className={styles.metricLabel}>Uptime</div>
                    <div className={styles.metricValue}>
                      {formatUptime(status.uptime)}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Configuration */}
            {config && (
              <div className={styles.card}>
                <h2>Configuration</h2>
                <div className={styles.config}>
                  {Object.entries(config).map(([key, value]) => (
                    <div key={key} className={styles.configRow}>
                      <span className={styles.label}>{formatLabel(key)}</span>
                      <span className={styles.value}>{JSON.stringify(value)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

function formatUptime(seconds: number) {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  return `${days}d ${hours}h ${minutes}m`;
}

function formatLabel(key: string) {
  return key
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}
