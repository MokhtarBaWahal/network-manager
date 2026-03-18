import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { deviceApi } from '../api';
import Loading from '../components/Loading';
import { useLanguage } from '../i18n/LanguageContext';
import styles from './DeviceDetail.module.css';

export default function DeviceClients() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { t } = useLanguage();
  const [clients, setClients] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    if (id) {
      deviceApi.getClients(id)
        .then(r => setClients(Array.isArray(r.data) ? r.data : []))
        .catch(() => {})
        .finally(() => setLoading(false));
    }
  }, [id]);

  const filtered = clients.filter(c => {
    const q = search.toLowerCase();
    return (
      (c['host-name'] || c['hostname'] || '').toLowerCase().includes(q) ||
      (c['address'] || '').includes(q) ||
      (c['mac-address'] || '').toLowerCase().includes(q)
    );
  });

  if (loading) return <Loading />;

  return (
    <div className={styles.detail}>
      <button className={styles.backButton} onClick={() => navigate(`/devices/${id}`)}>
        <ArrowLeft size={20} />
        {t('clients.backToDevice')}
      </button>

      <div className={styles.header}>
        <h1>{t('clients.title')}</h1>
        <span className={styles.badge}>{t('clients.total', { n: clients.length })}</span>
      </div>

      <div className={styles.card}>
        <div style={{ marginBottom: '1rem' }}>
          <input
            type="text"
            placeholder={t('clients.search')}
            value={search}
            onChange={e => setSearch(e.target.value)}
            style={{ width: '100%', padding: '0.625rem 0.75rem', fontSize: '0.875rem', minHeight: '44px' }}
          />
        </div>

        {filtered.length === 0 ? (
          <p className={styles.sectionEmpty}>
            {search ? t('clients.noResults') : t('clients.noDhcp')}
          </p>
        ) : (
          <div className={styles.tableScroll}>
            <table className={styles.table}>
              <thead>
                <tr className={styles.tableHeader}>
                  <th>{t('device.hostname')}</th>
                  <th>{t('device.ip')}</th>
                  <th>{t('clients.mac')}</th>
                  <th>{t('device.status')}</th>
                  <th>{t('clients.expires')}</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((c, i) => (
                  <tr key={i} className={styles.tableRow}>
                    <td>{c['host-name'] || c['hostname'] || '—'}</td>
                    <td>{c['address'] || '—'}</td>
                    <td className={styles.tdMono}>{c['mac-address'] || '—'}</td>
                    <td className={c['status'] === 'bound' ? styles.tdGreen : styles.tdMuted}>
                      {c['status'] || '—'}
                    </td>
                    <td className={styles.tdMuted}>{c['expires-after'] || '—'}</td>
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
