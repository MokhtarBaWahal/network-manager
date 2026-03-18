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
  googleAuth: (idToken: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  loading: boolean;
}

const AuthContext = createContext<AuthContextValue>(null!);

function _storeSession(accessToken: string, userData: User, setUser: (u: User) => void) {
  localStorage.setItem('token', accessToken);
  api.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
  setUser(userData);
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

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
    _storeSession(res.data.access_token, res.data.user, setUser);
  }

  async function register(username: string, password: string) {
    const res = await api.post('/auth/register', { username, password });
    _storeSession(res.data.access_token, res.data.user, setUser);
  }

  async function googleAuth(idToken: string) {
    const res = await api.post('/auth/google', { id_token: idToken });
    _storeSession(res.data.access_token, res.data.user, setUser);
  }

  function logout() {
    localStorage.removeItem('token');
    delete api.defaults.headers.common['Authorization'];
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, login, register, googleAuth, logout, isAuthenticated: !!user, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
