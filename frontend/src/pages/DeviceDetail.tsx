import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, RefreshCw, Power, Trash2 } from 'lucide-react';
import { deviceApi, Device, DeviceStatus } from '../api';
import Loading from '../components/Loading';
import { useLanguage } from '../i18n/LanguageContext';
import styles from './DeviceDetail.module.css';

export default function DeviceDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { t } = useLanguage();
  const [device, setDevice] = useState<Device | null>(null);
  const [status, setStatus] = useState<DeviceStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [actionLoading, setActionLoading] = useState(false);
  const [clients, setClients] = useState<any[]>([]);
  const [interfaces, setInterfaces] = useState<any[]>([]);
  const [health, setHealth] = useState<Record<string, any>>({});

  useEffect(() => {
    if (id) {
      fetchDevice();
      fetchStatus();
      deviceApi.getClients(id).then(r => setClients(Array.isArray(r.data) ? r.data : [])).catch(() => {});
      deviceApi.getInterfaces(id).then(r => setInterfaces(r.data?.interfaces || [])).catch(() => {});
      deviceApi.getHealth(id).then(r => setHealth(r.data && typeof r.data === 'object' ? r.data : {})).catch(() => {});
    }
  }, [id]);

  async function fetchDevice() {
    try {
      const res = await deviceApi.get(id!);
      setDevice(res.data);
    } catch (err) {
      setError(t('device.loadError'));
    }
  }

  async function fetchStatus() {
    try {
      const statusRes = await deviceApi.refresh(id!);
      const data = statusRes.data as any;
      setStatus(data.device || data);

      setLoading(false);
    } catch (err) {
      setError(t('device.statusError'));
      setLoading(false);
    }
  }

  async function handleReboot() {
    setActionLoading(true);
    try {
      await deviceApi.reboot(id!);
      alert(t('device.rebootOk'));
      fetchStatus();
    } catch (err) {
      alert(t('device.rebootFail'));
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

  async function handleDelete() {
    const confirmed = window.confirm(
      t('device.deleteConfirm', { name: device?.name ?? '' })
    );
    
    if (!confirmed) return;

    setActionLoading(true);
    try {
      await deviceApi.delete(id!);
      alert(t('device.deleteOk'));
      navigate('/');
    } catch (err) {
      alert(t('device.deleteFail'));
    } finally {
      setActionLoading(false);
    }
  }

  if (loading) return <Loading />;

  return (
    <div className={styles.detail}>
      <button className={styles.backButton} onClick={() => navigate('/')}>
        <ArrowLeft size={20} />
        {t('btn.back')}
      </button>

      {error && <div className={styles.error}>{error}</div>}

      {device && (
        <>
          <div className={styles.header}>
            <h1>{device.name}</h1>
            <div className={styles.actions}>
              {status && (
                <>
                  <button
                    className={`${styles.btn} ${styles.secondary}`}
                    onClick={handleRefresh}
                    disabled={actionLoading}
                  >
                    <RefreshCw size={18} />
                    {t('btn.refresh')}
                  </button>
                  <button
                    className={`${styles.btn} ${styles.danger}`}
                    onClick={handleReboot}
                    disabled={actionLoading}
                  >
                    <Power size={18} />
                    {t('btn.reboot')}
                  </button>
                </>
              )}
              <button
                className={`${styles.btn} ${styles.delete}`}
                onClick={handleDelete}
                disabled={actionLoading}
              >
                <Trash2 size={18} />
                {t('btn.delete')}
              </button>
            </div>
          </div>

          <div className={styles.grid}>
            {/* Device Information */}
            <div className={styles.card}>
              <h2>{t('device.info')}</h2>
              <div className={styles.info}>
                <div className={styles.infoRow}>
                  <span className={styles.label}>{t('device.type')}</span>
                  <span className={styles.value}>{device.device_type}</span>
                </div>
                <div className={styles.infoRow}>
                  <span className={styles.label}>{t('device.ip')}</span>
                  <span className={styles.value}>{device.ip_address}</span>
                </div>
                <div className={styles.infoRow}>
                  <span className={styles.label}>{t('device.location')}</span>
                  <span className={styles.value}>{device.location || t('device.locationNone')}</span>
                </div>
                {status && (
                  <div className={styles.infoRow}>
                    <span className={styles.label}>{t('device.status')}</span>
                    <span className={`${styles.value} ${styles[status.status]}`}>
                      {status.status}
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* System Metrics */}
            {status && (
              <div className={styles.card}>
                <h2>{t('device.metrics')}</h2>
                <div className={styles.metrics}>
                  {status.cpu_usage !== undefined && (
                    <div className={styles.metric}>
                      <div className={styles.metricLabel}>{t('device.cpu')}</div>
                      <div className={styles.metricValue}>{status.cpu_usage?.toFixed(1)}%</div>
                      <div className={styles.metricBar}>
                        <div
                          className={
                            status.cpu_usage > 80 ? styles.metricFillDanger
                            : status.cpu_usage > 60 ? styles.metricFillWarn
                            : styles.metricFill
                          }
                          style={{ width: `${status.cpu_usage}%` }}
                        ></div>
                      </div>
                    </div>
                  )}
                  {status.memory_usage !== undefined && (
                    <div className={styles.metric}>
                      <div className={styles.metricLabel}>{t('device.memory')}</div>
                      <div className={styles.metricValue}>{status.memory_usage?.toFixed(1)}%</div>
                      <div className={styles.metricBar}>
                        <div
                          className={
                            status.memory_usage > 80 ? styles.metricFillDanger
                            : status.memory_usage > 60 ? styles.metricFillWarn
                            : styles.metricFill
                          }
                          style={{ width: `${status.memory_usage}%` }}
                        ></div>
                      </div>
                    </div>
                  )}
                  {status.uptime !== undefined && (
                    <div className={styles.metric}>
                      <div className={styles.metricLabel}>{t('device.uptime')}</div>
                      <div className={styles.metricValue}>
                        {formatUptime(status.uptime)}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Connected Devices */}
            <div className={styles.card}>
              <div className={styles.cardHeader}>
                <h2>{t('device.connectedDevices')}</h2>
                {clients.length > 0 && <span className={styles.badge}>{clients.length}</span>}
              </div>
              {clients.length === 0 ? (
                <p className={styles.sectionEmpty}>{t('device.noDhcp')}</p>
              ) : (
                <>
                  <div className={styles.tableScroll}>
                    <table className={styles.table}>
                      <thead>
                        <tr className={styles.tableHeader}>
                          <th>{t('device.hostname')}</th>
                          <th>{t('device.ip')}</th>
                          <th>{t('device.status')}</th>
                        </tr>
                      </thead>
                      <tbody>
                        {clients.slice(0, 5).map((c, i) => (
                          <tr key={i} className={styles.tableRow}>
                            <td>{c['host-name'] || c['hostname'] || '—'}</td>
                            <td>{c['address'] || '—'}</td>
                            <td className={c['status'] === 'bound' ? styles.tdGreen : styles.tdMuted}>
                              {c['status'] || '—'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  {clients.length > 5 && (
                    <Link to={`/devices/${id}/clients`} className={styles.viewAllLink}>
                      {t('device.viewAllDevices', { n: clients.length })}
                    </Link>
                  )}
                </>
              )}
            </div>

            {/* Interface Stats */}
            <div className={styles.card}>
              <div className={styles.cardHeader}>
                <h2>{t('device.interfaces')}</h2>
                {interfaces.length > 0 && <span className={styles.badge}>{interfaces.length}</span>}
              </div>
              {interfaces.length === 0 ? (
                <p className={styles.sectionEmpty}>{t('device.noIfaceData')}</p>
              ) : (
                <>
                  <div className={styles.tableScroll}>
                    <table className={styles.table}>
                      <thead>
                        <tr className={styles.tableHeader}>
                          <th>Interface</th>
                          <th>{t('device.running')}</th>
                          <th className={styles.tdRight}>{t('device.rx')}</th>
                          <th className={styles.tdRight}>{t('device.tx')}</th>
                        </tr>
                      </thead>
                      <tbody>
                        {interfaces.slice(0, 5).map((iface, i) => (
                          <tr key={i} className={styles.tableRow}>
                            <td>{iface.name}</td>
                            <td className={iface.running === 'true' || iface.running === true ? styles.tdGreen : styles.tdRed}>
                              {iface.running === 'true' || iface.running === true ? t('device.yes') : t('device.no')}
                            </td>
                            <td className={styles.tdRight}>{formatBytes(iface.rx_bytes)}</td>
                            <td className={styles.tdRight}>{formatBytes(iface.tx_bytes)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  {interfaces.length > 5 && (
                    <Link to={`/devices/${id}/interfaces`} className={styles.viewAllLink}>
                      {t('device.viewAllIfaces', { n: interfaces.length })}
                    </Link>
                  )}
                </>
              )}
            </div>

            {/* System Health */}
            {Object.keys(health).length > 0 && (
              <div className={styles.card}>
                <h2>{t('device.health')}</h2>
                <div className={styles.info}>
                  {Object.entries(health).map(([key, val]) => (
                    <div key={key} className={styles.infoRow}>
                      <span className={styles.label}>{key}</span>
                      <span className={styles.value}>{String(val)}</span>
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

function formatBytes(bytes: number): string {
  if (!bytes) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${units[i]}`;
}

function formatLabel(key: string) {
  return key
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}
