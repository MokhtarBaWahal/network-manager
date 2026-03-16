import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Activity, Wifi, Zap, AlertCircle, Beaker } from 'lucide-react';
import { dashboardApi, Device, DashboardStats, Alert } from '../api';
import StatCard from '../components/StatCard';
import DeviceCard from '../components/DeviceCard';
import AlertList from '../components/AlertList';
import Loading from '../components/Loading';
import styles from './Dashboard.module.css';

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [devices, setDevices] = useState<Device[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval);
  }, []);

  async function fetchData() {
    try {
      const dashRes = await dashboardApi.getDashboard();

      setStats(dashRes.data.stats);
      setDevices(dashRes.data.devices);
      setAlerts(dashRes.data.recent_alerts.slice(0, 5)); // Show top 5 alerts
      setError('');
      setLoading(false);
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error(err);
      setLoading(false);
    }
  }

  if (loading && !stats) {
    return <Loading />;
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>Dashboard</h1>
        <Link to="/test-vpn" className={styles.testLink}>
          <Beaker size={16} />
          Test VPN Setup
        </Link>
      </div>

      {error && <div className={styles.error}>{error}</div>}

      {/* Stats Grid */}
      <div className={styles.statsGrid}>
        <StatCard
          icon={<Wifi size={24} />}
          title="Total Devices"
          value={stats?.total_devices ?? 0}
          color="blue"
        />
        <StatCard
          icon={<Activity size={24} />}
          title="Online Devices"
          value={stats?.online_devices ?? 0}
          color="green"
          subtitle={`${((stats?.online_devices ?? 0) / (stats?.total_devices ?? 1) * 100).toFixed(0)}% uptime`}
        />
        <StatCard
          icon={<AlertCircle size={24} />}
          title="Offline Devices"
          value={stats?.offline_devices ?? 0}
          color="red"
        />
        <StatCard
          icon={<Zap size={24} />}
          title="Avg Latency"
          value={stats?.avg_latency ? `${stats.avg_latency.toFixed(1)}ms` : 'N/A'}
          color="yellow"
        />
      </div>

      <div className={styles.contentGrid}>
        {/* Devices Section */}
        <section className={styles.section}>
          <div className={styles.sectionHeader}>
            <h2>Devices</h2>
            <Link to="/add-device" className={styles.link}>
              + Add Device
            </Link>
          </div>

          {devices.length === 0 ? (
            <div className={styles.empty}>
              <p>No devices yet. <Link to="/add-device">Add your first device</Link></p>
            </div>
          ) : (
            <div className={styles.deviceGrid}>
              {devices.map((device) => (
                <Link
                  key={device.id}
                  to={`/devices/${device.id}`}
                  className={styles.deviceLink}
                >
                  <DeviceCard device={device} />
                </Link>
              ))}
            </div>
          )}
        </section>

        {/* Alerts Section */}
        {alerts.length > 0 && (
          <section className={styles.section}>
            <div className={styles.sectionHeader}>
              <h2>Recent Alerts</h2>
            </div>
            <AlertList alerts={alerts} />
          </section>
        )}
      </div>
    </div>
  );
}
