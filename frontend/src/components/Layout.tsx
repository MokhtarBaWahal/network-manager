import { Outlet, Link, useLocation } from 'react-router-dom';
import { Network, Plus, Home } from 'lucide-react';
import styles from './Layout.module.css';

export default function Layout() {
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div className={styles.headerContent}>
          <div className={styles.logo}>
            <Network size={28} />
            <h1>Network Manager</h1>
          </div>
          <nav className={styles.nav}>
            <Link
              to="/"
              className={`${styles.navLink} ${isActive('/') ? styles.active : ''}`}
            >
              <Home size={20} />
              Dashboard
            </Link>
            <Link
              to="/add-device"
              className={`${styles.navLink} ${isActive('/add-device') ? styles.active : ''}`}
            >
              <Plus size={20} />
              Add Device
            </Link>
          </nav>
        </div>
      </header>

      <main className={styles.main}>
        <Outlet />
      </main>

      <footer className={styles.footer}>
        <p>&copy; 2026 Network Manager. All rights reserved.</p>
      </footer>
    </div>
  );
}
