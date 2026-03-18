import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Activity, Wifi, Zap, AlertCircle, Beaker } from 'lucide-react';
import { dashboardApi, Device, DashboardStats, Alert } from '../api';
import StatCard from '../components/StatCard';
import DeviceCard from '../components/DeviceCard';
import AlertList from '../components/AlertList';
import Loading from '../components/Loading';
import { useLanguage } from '../i18n/LanguageContext';
import styles from './Dashboard.module.css';

export default function Dashboard() {
  const { t } = useLanguage();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [devices, setDevices] = useState<Device[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  async function fetchData() {
    try {
      const dashRes = await dashboardApi.getDashboard();
      setStats(dashRes.data.stats);
      setDevices(dashRes.data.devices);
      setAlerts(dashRes.data.recent_alerts.slice(0, 5));
      setError('');
      setLoading(false);
    } catch (err) {
      setError(t('dash.error'));
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
        <h1>{t('dash.title')}</h1>
        <Link to="/test-vpn" className={styles.testLink}>
          <Beaker size={16} />
          {t('dash.testVpn')}
        </Link>
      </div>

      {error && <div className={styles.error}>{error}</div>}

      <div className={styles.statsGrid}>
        <StatCard
          icon={<Wifi size={24} />}
          title={t('dash.totalDevices')}
          value={stats?.total_devices ?? 0}
          color="blue"
        />
        <StatCard
          icon={<Activity size={24} />}
          title={t('dash.online')}
          value={stats?.online_devices ?? 0}
          color="green"
          subtitle={`${((stats?.online_devices ?? 0) / (stats?.total_devices ?? 1) * 100).toFixed(0)}${t('dash.uptime')}`}
        />
        <StatCard
          icon={<AlertCircle size={24} />}
          title={t('dash.offline')}
          value={stats?.offline_devices ?? 0}
          color="red"
        />
        <StatCard
          icon={<Zap size={24} />}
          title={t('dash.latency')}
          value={stats?.avg_latency ? `${stats.avg_latency.toFixed(1)}ms` : t('dash.na')}
          color="yellow"
        />
      </div>

      <div className={styles.contentGrid}>
        <section className={styles.section}>
          <div className={styles.sectionHeader}>
            <h2>{t('dash.devices')}</h2>
            <Link to="/add-device" className={styles.link}>
              {t('dash.addDevice')}
            </Link>
          </div>

          {devices.length === 0 ? (
            <div className={styles.empty}>
              <p>{t('dash.noDevices')} <Link to="/add-device">{t('dash.addFirst')}</Link></p>
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

        {alerts.length > 0 && (
          <section className={styles.section}>
            <div className={styles.sectionHeader}>
              <h2>{t('dash.alerts')}</h2>
            </div>
            <AlertList alerts={alerts} />
          </section>
        )}
      </div>
    </div>
  );
}
