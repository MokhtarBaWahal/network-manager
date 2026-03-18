import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { LanguageProvider } from './i18n/LanguageContext';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import DeviceDetail from './pages/DeviceDetail';
import DeviceClients from './pages/DeviceClients';
import DeviceInterfaces from './pages/DeviceInterfaces';
import AddDevice from './pages/AddDevice';
import TestVPN from './pages/TestVPN';
import './App.css';

// Vercel deployment trigger

function App() {
  return (
    <LanguageProvider>
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/devices/:id" element={<DeviceDetail />} />
          <Route path="/devices/:id/clients" element={<DeviceClients />} />
          <Route path="/devices/:id/interfaces" element={<DeviceInterfaces />} />
          <Route path="/add-device" element={<AddDevice />} />
          <Route path="/test-vpn" element={<TestVPN />} />
        </Route>
      </Routes>
    </BrowserRouter>
    </LanguageProvider>
  );
}

export default App;
