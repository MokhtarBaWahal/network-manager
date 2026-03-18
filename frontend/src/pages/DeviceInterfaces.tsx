import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { deviceApi } from '../api';
import Loading from '../components/Loading';
import { useLanguage } from '../i18n/LanguageContext';
import styles from './DeviceDetail.module.css';

function formatBytes(bytes: number): string {
  if (!bytes) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${units[i]}`;
}

export default function DeviceInterfaces() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { t } = useLanguage();
  const [interfaces, setInterfaces] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'running' | 'down'>('all');

  useEffect(() => {
    if (id) {
      deviceApi.getInterfaces(id)
        .then(r => setInterfaces(r.data?.interfaces || []))
        .catch(() => {})
        .finally(() => setLoading(false));
    }
  }, [id]);

  const isRunning = (iface: any) => iface.running === 'true' || iface.running === true;

  const filtered = interfaces.filter(iface => {
    if (filter === 'running') return isRunning(iface);
    if (filter === 'down') return !isRunning(iface);
    return true;
  });

  const runningCount = interfaces.filter(isRunning).length;

  if (loading) return <Loading />;

  return (
    <div className={styles.detail}>
      <button className={styles.backButton} onClick={() => navigate(`/devices/${id}`)}>
        <ArrowLeft size={20} />
        {t('ifaces.backToDevice')}
      </button>

      <div className={styles.header}>
        <h1>{t('ifaces.title')}</h1>
        <span className={styles.badge}>{t('ifaces.total', { n: interfaces.length })}</span>
      </div>

      <div className={styles.card}>
        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
          {(['all', 'running', 'down'] as const).map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`${styles.btn} ${filter === f ? '' : styles.secondary}`}
              style={{ padding: '0.625rem 0.875rem', fontSize: '0.8rem', minHeight: '44px' }}
            >
              {f === 'all'
                ? t('ifaces.all', { n: interfaces.length })
                : f === 'running'
                ? t('ifaces.up', { n: runningCount })
                : t('ifaces.down', { n: interfaces.length - runningCount })}
            </button>
          ))}
        </div>

        {filtered.length === 0 ? (
          <p className={styles.sectionEmpty}>{t('ifaces.noMatch')}</p>
        ) : (
          <div className={styles.tableScroll}>
            <table className={styles.table}>
              <thead>
                <tr className={styles.tableHeader}>
                  <th>Interface</th>
                  <th>{t('ifaces.type')}</th>
                  <th>{t('device.running')}</th>
                  <th className={styles.tdRight}>{t('ifaces.rxBytes')}</th>
                  <th className={styles.tdRight}>{t('ifaces.txBytes')}</th>
                  <th className={styles.tdRight}>{t('ifaces.rxPkts')}</th>
                  <th className={styles.tdRight}>{t('ifaces.txPkts')}</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((iface, i) => (
                  <tr key={i} className={styles.tableRow}>
                    <td>{iface.name}</td>
                    <td className={styles.tdMuted}>{iface.type || '—'}</td>
                    <td className={isRunning(iface) ? styles.tdGreen : styles.tdRed}>
                      {isRunning(iface) ? t('device.yes') : t('device.no')}
                    </td>
                    <td className={styles.tdRight}>{formatBytes(iface.rx_bytes)}</td>
                    <td className={styles.tdRight}>{formatBytes(iface.tx_bytes)}</td>
                    <td className={styles.tdRight}>{iface['rx-packet'] ?? iface.rx_packets ?? '—'}</td>
                    <td className={styles.tdRight}>{iface['tx-packet'] ?? iface.tx_packets ?? '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
