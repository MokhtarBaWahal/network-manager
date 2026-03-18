import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Plus } from 'lucide-react';
import { deviceApi } from '../api';
import { useLanguage } from '../i18n/LanguageContext';
import styles from './AddDevice.module.css';

export default function AddDevice() {
  const navigate = useNavigate();
  const { t } = useLanguage();
  const [formData, setFormData] = useState({
    name: '',
    device_type: 'starlink' as 'starlink' | 'mikrotik',
    ip_address: '',
    location: '',
    username: '',
    password: '',
    port: '',
    api_type: 'auto' as 'auto' | 'binary' | 'rest',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const credentials: any = {};
      if (formData.username) credentials.username = formData.username;
      if (formData.password) credentials.password = formData.password;
      if (formData.port) credentials.port = parseInt(formData.port);
      if (formData.device_type === 'mikrotik' && formData.api_type) credentials.api_type = formData.api_type;

      let ip = formData.ip_address.trim();
      if (ip.startsWith('http://')) ip = ip.substring(7);
      if (ip.startsWith('https://')) ip = ip.substring(8);

      await deviceApi.create({
        name: formData.name,
        device_type: formData.device_type,
        ip_address: ip,
        location: formData.location,
        credentials: Object.keys(credentials).length > 0 ? credentials : undefined,
      });

      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || t('add.error'));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.container}>
      <button className={styles.backButton} onClick={() => navigate('/')}>
        <ArrowLeft size={20} />
        {t('add.back')}
      </button>

      <div className={styles.card}>
        <h1>{t('add.title')}</h1>

        {error && <div className={styles.error}>{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className={styles.formGroup}>
            <label>{t('add.name')}</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder={t('add.namePh')}
              required
            />
          </div>

          <div className={styles.formGroup}>
            <label>{t('add.type')}</label>
            <select
              name="device_type"
              value={formData.device_type}
              onChange={handleChange}
              required
            >
              <option value="starlink">{t('add.starlink')}</option>
              <option value="mikrotik">{t('add.mikrotik')}</option>
            </select>
          </div>

          <div className={styles.formGroup}>
            <label>{t('add.ip')}</label>
            <input
              type="text"
              name="ip_address"
              value={formData.ip_address}
              onChange={handleChange}
              placeholder="192.168.100.1"
              required
            />
          </div>

          <div className={styles.formGroup}>
            <label>{t('add.location')}</label>
            <input
              type="text"
              name="location"
              value={formData.location}
              onChange={handleChange}
              placeholder={t('add.locationPh')}
            />
          </div>

          {formData.device_type === 'mikrotik' && (
            <>
              <div className={styles.divider}>{t('add.credentials')}</div>

              <div className={styles.formGroup}>
                <label>{t('add.username')}</label>
                <input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  placeholder="admin"
                />
              </div>

              <div className={styles.formGroup}>
                <label>{t('add.password')}</label>
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="••••••••"
                />
              </div>

              <div className={styles.formGroup}>
                <label>{t('add.port')}</label>
                <input
                  type="number"
                  name="port"
                  value={formData.port}
                  onChange={handleChange}
                  placeholder="80"
                />
              </div>

              <div className={styles.formGroup}>
                <label>{t('add.apiType')}</label>
                <select name="api_type" value={formData.api_type} onChange={handleChange}>
                  <option value="auto">{t('add.apiAuto')}</option>
                  <option value="binary">{t('add.apiBinary')}</option>
                  <option value="rest">{t('add.apiRest')}</option>
                </select>
              </div>
            </>
          )}

          <div className={styles.actions}>
            <button type="button" className={styles.btnCancel} onClick={() => navigate('/')}>
              {t('add.cancel')}
            </button>
            <button type="submit" className={styles.btnSubmit} disabled={loading}>
              <Plus size={18} />
              {loading ? t('add.submitting') : t('add.submit')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
