import { AlertCircle, CheckCircle, Info } from 'lucide-react';
import { Alert } from '../api';
import styles from './AlertList.module.css';

interface AlertListProps {
  alerts: Alert[];
}

export default function AlertList({ alerts }: AlertListProps) {
  const getIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
      case 'error':
        return <AlertCircle size={16} />;
      case 'warning':
        return <AlertCircle size={16} />;
      default:
        return <Info size={16} />;
    }
  };

  return (
    <div className={styles.list}>
      {alerts.map((alert) => (
        <div key={alert.id} className={`${styles.item} ${styles[alert.severity]}`}>
          <div className={styles.iconWrapper}>{getIcon(alert.severity)}</div>
          <div className={styles.content}>
            <p className={styles.message}>{alert.message}</p>
            <p className={styles.time}>
              {new Date(alert.created_at).toLocaleString()}
            </p>
          </div>
          {alert.resolved && (
            <div className={styles.resolved}>
              <CheckCircle size={16} />
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
