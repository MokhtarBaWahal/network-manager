import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import api from '../api';

interface User {
  id: string;
  username: string;
}

interface AuthContextValue {
  user: User | null;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  loading: boolean;
}

const AuthContext = createContext<AuthContextValue>(null!);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // On mount, restore session from localStorage
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      api.get('/auth/me')
        .then(res => setUser(res.data))
        .catch(() => {
          localStorage.removeItem('token');
          delete api.defaults.headers.common['Authorization'];
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  async function login(username: string, password: string) {
    const res = await api.post('/auth/login', { username, password });
    const { access_token, user: userData } = res.data;
    localStorage.setItem('token', access_token);
    api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
    setUser(userData);
  }

  async function register(username: string, password: string) {
    const res = await api.post('/auth/register', { username, password });
    const { access_token, user: userData } = res.data;
    localStorage.setItem('token', access_token);
    api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
    setUser(userData);
  }

  function logout() {
    localStorage.removeItem('token');
    delete api.defaults.headers.common['Authorization'];
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, login, register, logout, isAuthenticated: !!user, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
