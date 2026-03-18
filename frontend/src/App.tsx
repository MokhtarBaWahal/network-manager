import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { LanguageProvider } from './i18n/LanguageContext';
import { AuthProvider, useAuth } from './context/AuthContext';
import Layout from './components/Layout';
import Loading from './components/Loading';
import Dashboard from './pages/Dashboard';
import DeviceDetail from './pages/DeviceDetail';
import DeviceClients from './pages/DeviceClients';
import DeviceInterfaces from './pages/DeviceInterfaces';
import AddDevice from './pages/AddDevice';
import TestVPN from './pages/TestVPN';
import Login from './pages/Login';
import Register from './pages/Register';
import './App.css';

function AuthLayout() {
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();
  if (loading) return <Loading />;
  if (!isAuthenticated) return <Navigate to="/login" state={{ from: location }} replace />;
  return <Layout />;
}

function App() {
  return (
    <LanguageProvider>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route element={<AuthLayout />}>
              <Route path="/" element={<Dashboard />} />
              <Route path="/devices/:id" element={<DeviceDetail />} />
              <Route path="/devices/:id/clients" element={<DeviceClients />} />
              <Route path="/devices/:id/interfaces" element={<DeviceInterfaces />} />
              <Route path="/add-device" element={<AddDevice />} />
              <Route path="/test-vpn" element={<TestVPN />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </LanguageProvider>
  );
}

export default App;
