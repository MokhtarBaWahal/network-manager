import styles from './StatCard.module.css';

interface StatCardProps {
  icon: React.ReactNode;
  title: string;
  value: string | number;
  subtitle?: string;
  color?: 'blue' | 'green' | 'red' | 'yellow';
}

export default function StatCard({ icon, title, value, subtitle, color = 'blue' }: StatCardProps) {
  return (
    <div className={`${styles.card} ${styles[color]}`}>
      <div className={styles.icon}>{icon}</div>
      <div className={styles.content}>
        <p className={styles.title}>{title}</p>
        <p className={styles.value}>{value}</p>
        {subtitle && <p className={styles.subtitle}>{subtitle}</p>}
      </div>
    </div>
  );
}
