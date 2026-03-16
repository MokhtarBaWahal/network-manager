import { Wifi, Zap, Circle } from 'lucide-react';
import { Device } from '../api';
import styles from './DeviceCard.module.css';

interface DeviceCardProps {
  device: Device;
}

export default function DeviceCard({ device }: DeviceCardProps) {
  const statusColor = {
    online: '#10b981',
    offline: '#ef4444',
    error: '#f59e0b',
  };

  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <h3>{device.name}</h3>
        <div className={styles.statusBadge} style={{ backgroundColor: statusColor[device.status] }}>
          <Circle size={8} fill="currentColor" />
          {device.status}
        </div>
      </div>

      <div className={styles.details}>
        <div className={styles.detail}>
          <span className={styles.label}>Type</span>
          <span className={styles.value}>
            {device.device_type === 'starlink' ? <Wifi size={16} /> : <Zap size={16} />}
            {device.device_type}
          </span>
        </div>
        <div className={styles.detail}>
          <span className={styles.label}>IP Address</span>
          <span className={styles.value}>{device.ip_address}</span>
        </div>
        <div className={styles.detail}>
          <span className={styles.label}>Location</span>
          <span className={styles.value}>{device.location || 'Not specified'}</span>
        </div>
      </div>

      <div className={styles.footer}>
        <span className={styles.link}>View Details →</span>
      </div>
    </div>
  );
}
