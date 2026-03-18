import { useState, FormEvent } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Network, LogIn } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../i18n/LanguageContext';
import styles from './Login.module.css';

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();
  const { t } = useLanguage();

  const from = (location.state as any)?.from?.pathname || '/';

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await login(username, password);
      navigate(from, { replace: true });
    } catch (err: any) {
      setError(err.response?.data?.detail || t('auth.loginError'));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        <div className={styles.logo}>
          <Network size={32} />
          <span>{t('app.name')}</span>
        </div>

        <h1 className={styles.title}>{t('auth.loginTitle')}</h1>

        {error && <div className={styles.error}>{error}</div>}

        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.formGroup}>
            <label>{t('auth.username')}</label>
            <input
              type="text"
              value={username}
              onChange={e => setUsername(e.target.value)}
              placeholder={t('auth.usernamePh')}
              autoComplete="username"
              required
            />
          </div>

          <div className={styles.formGroup}>
            <label>{t('auth.password')}</label>
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="••••••••"
              autoComplete="current-password"
              required
            />
          </div>

          <button type="submit" className={styles.btnSubmit} disabled={loading}>
            <LogIn size={18} />
            {loading ? t('auth.signingIn') : t('auth.loginBtn')}
          </button>
        </form>

        <p className={styles.switchLink}>
          {t('auth.noAccount')}{' '}
          <Link to="/register">{t('auth.registerLink')}</Link>
        </p>
      </div>
    </div>
  );
}
