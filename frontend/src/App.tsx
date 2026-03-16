import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import DeviceDetail from './pages/DeviceDetail';
import AddDevice from './pages/AddDevice';
import TestVPN from './pages/TestVPN';
import './App.css';

// Vercel deployment trigger

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/devices/:id" element={<DeviceDetail />} />
          <Route path="/add-device" element={<AddDevice />} />
          <Route path="/test-vpn" element={<TestVPN />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
