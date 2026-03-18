import { useState } from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { Network, Plus, Home, Menu, X } from 'lucide-react';
import { useLanguage } from '../i18n/LanguageContext';
import styles from './Layout.module.css';

export default function Layout() {
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);
  const { lang, setLang, t } = useLanguage();

  const isActive = (path: string) => location.pathname === path;
  const closeMenu = () => setMenuOpen(false);

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div className={styles.headerContent}>
          <div className={styles.logo}>
            <Network size={28} />
            <h1>{t('app.name')}</h1>
          </div>

          <div className={styles.headerActions}>
            <button
              className={styles.langToggle}
              onClick={() => setLang(lang === 'en' ? 'ar' : 'en')}
              aria-label="Switch language"
            >
              {lang === 'en' ? 'ع' : 'EN'}
            </button>

            <button
              className={styles.hamburger}
              onClick={() => setMenuOpen(o => !o)}
              aria-label={t('nav.toggleMenu') ?? 'Toggle menu'}
            >
              {menuOpen ? <X size={22} /> : <Menu size={22} />}
            </button>
          </div>

          <nav className={`${styles.nav} ${menuOpen ? styles.navOpen : ''}`}>
            <Link
              to="/"
              className={`${styles.navLink} ${isActive('/') ? styles.active : ''}`}
              onClick={closeMenu}
            >
              <Home size={20} />
              {t('nav.dashboard')}
            </Link>
            <Link
              to="/add-device"
              className={`${styles.navLink} ${isActive('/add-device') ? styles.active : ''}`}
              onClick={closeMenu}
            >
              <Plus size={20} />
              {t('nav.addDevice')}
            </Link>
          </nav>
        </div>
      </header>

      <main className={styles.main}>
        <Outlet />
      </main>

      <footer className={styles.footer}>
        <p>{t('footer.copy')}</p>
      </footer>
    </div>
  );
}
