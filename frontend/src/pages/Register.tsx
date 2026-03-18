import { useState, FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Network, UserPlus } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../i18n/LanguageContext';
import styles from './Login.module.css';

export default function Register() {
  const navigate = useNavigate();
  const { register } = useAuth();
  const { t } = useLanguage();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (password !== confirm) {
      setError(t('auth.passwordMismatch'));
      return;
    }
    setLoading(true);
    setError('');
    try {
      await register(username, password);
      navigate('/', { replace: true });
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      if (detail?.includes('taken')) {
        setError(t('auth.usernameTaken'));
      } else {
        setError(detail || t('auth.registerError'));
      }
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

        <h1 className={styles.title}>{t('auth.registerTitle')}</h1>

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
              minLength={3}
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
              autoComplete="new-password"
              minLength={6}
              required
            />
          </div>

          <div className={styles.formGroup}>
            <label>{t('auth.confirmPassword')}</label>
            <input
              type="password"
              value={confirm}
              onChange={e => setConfirm(e.target.value)}
              placeholder="••••••••"
              autoComplete="new-password"
              required
            />
          </div>

          <button type="submit" className={styles.btnSubmit} disabled={loading}>
            <UserPlus size={18} />
            {loading ? t('auth.registering') : t('auth.registerBtn')}
          </button>
        </form>

        <p className={styles.switchLink}>
          {t('auth.hasAccount')}{' '}
          <Link to="/login">{t('auth.loginLink')}</Link>
        </p>
      </div>
    </div>
  );
}
