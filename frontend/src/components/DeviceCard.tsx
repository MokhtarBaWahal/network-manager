import { Wifi, Zap, Circle } from 'lucide-react';
import { Device } from '../api';
import { useLanguage } from '../i18n/LanguageContext';
import styles from './DeviceCard.module.css';

interface DeviceCardProps {
  device: Device;
}

export default function DeviceCard({ device }: DeviceCardProps) {
  const { t } = useLanguage();
  const statusColor: { [key: string]: string } = {
    online: '#10b981',
    offline: '#ef4444',
    error: '#f59e0b',
    unknown: '#9ca3af',
  };

  return (
    <div className={`${styles.card} ${styles[device.device_type] || ''}`}>
      <div className={styles.header}>
        <h3>{device.name}</h3>
        <div className={styles.statusBadge} style={{ backgroundColor: statusColor[device.status] }}>
          <Circle size={8} fill="currentColor" />
          {device.status}
        </div>
      </div>

      <div className={styles.details}>
        <div className={styles.detail}>
          <span className={styles.label}>{t('card.type')}</span>
          <span className={styles.value}>
            {device.device_type === 'starlink' ? <Wifi size={16} /> : <Zap size={16} />}
            {device.device_type}
          </span>
        </div>
        <div className={styles.detail}>
          <span className={styles.label}>{t('card.ip')}</span>
          <span className={styles.value}>{device.ip_address}</span>
        </div>
        <div className={styles.detail}>
          <span className={styles.label}>{t('card.location')}</span>
          <span className={styles.value}>{device.location || t('card.locationNone')}</span>
        </div>
        {device.cpu_usage != null && (
          <div className={styles.detail}>
            <span className={styles.label}>{t('card.cpu')}</span>
            <div style={{ textAlign: 'right', flex: 1 }}>
              <span className={styles.value}>{device.cpu_usage.toFixed(1)}%</span>
              <div className={styles.miniBar}>
                <div
                  className={
                    device.cpu_usage > 80 ? styles.miniBarFillDanger
                    : device.cpu_usage > 60 ? styles.miniBarFillWarn
                    : styles.miniBarFill
                  }
                  style={{ width: `${device.cpu_usage}%` }}
                />
              </div>
            </div>
          </div>
        )}
        {device.memory_usage != null && (
          <div className={styles.detail}>
            <span className={styles.label}>{t('card.memory')}</span>
            <div style={{ textAlign: 'right', flex: 1 }}>
              <span className={styles.value}>{device.memory_usage.toFixed(1)}%</span>
              <div className={styles.miniBar}>
                <div
                  className={
                    device.memory_usage > 80 ? styles.miniBarFillDanger
                    : device.memory_usage > 60 ? styles.miniBarFillWarn
                    : styles.miniBarFill
                  }
                  style={{ width: `${device.memory_usage}%` }}
                />
              </div>
            </div>
          </div>
        )}
      </div>

      <div className={styles.footer}>
        <span className={styles.link}>{t('card.viewDetails')}</span>
      </div>
    </div>
  );
}
