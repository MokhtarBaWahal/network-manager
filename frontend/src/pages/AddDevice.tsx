import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Plus } from 'lucide-react';
import { deviceApi } from '../api';
import styles from './AddDevice.module.css';

export default function AddDevice() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    device_type: 'starlink' as 'starlink' | 'mikrotik',
    ip_address: '',
    location: '',
    username: '',
    password: '',
    port: '',
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

      await deviceApi.create({
        name: formData.name,
        device_type: formData.device_type,
        ip_address: formData.ip_address,
        location: formData.location,
        credentials: credentials || undefined,
      });

      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create device');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.container}>
      <button className={styles.backButton} onClick={() => navigate('/')}>
        <ArrowLeft size={20} />
        Back
      </button>

      <div className={styles.card}>
        <h1>Add New Device</h1>

        {error && <div className={styles.error}>{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className={styles.formGroup}>
            <label>Device Name *</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="e.g., Main Dish or Router 1"
              required
            />
          </div>

          <div className={styles.formGroup}>
            <label>Device Type *</label>
            <select
              name="device_type"
              value={formData.device_type}
              onChange={handleChange}
              required
            >
              <option value="starlink">Starlink Dish</option>
              <option value="mikrotik">MikroTik Router</option>
            </select>
          </div>

          <div className={styles.formGroup}>
            <label>IP Address *</label>
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
            <label>Location</label>
            <input
              type="text"
              name="location"
              value={formData.location}
              onChange={handleChange}
              placeholder="e.g., Rooftop, Office"
            />
          </div>

          {formData.device_type === 'mikrotik' && (
            <>
              <div className={styles.divider}>Router Credentials (Optional)</div>

              <div className={styles.formGroup}>
                <label>Username</label>
                <input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  placeholder="admin"
                />
              </div>

              <div className={styles.formGroup}>
                <label>Password</label>
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="••••••••"
                />
              </div>

              <div className={styles.formGroup}>
                <label>Port</label>
                <input
                  type="number"
                  name="port"
                  value={formData.port}
                  onChange={handleChange}
                  placeholder="80"
                />
              </div>
            </>
          )}

          <div className={styles.actions}>
            <button type="button" className={styles.btnCancel} onClick={() => navigate('/')}>
              Cancel
            </button>
            <button type="submit" className={styles.btnSubmit} disabled={loading}>
              <Plus size={18} />
              {loading ? 'Adding...' : 'Add Device'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
