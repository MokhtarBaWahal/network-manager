import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import DeviceDetail from './pages/DeviceDetail';
import AddDevice from './pages/AddDevice';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/devices/:id" element={<DeviceDetail />} />
          <Route path="/add-device" element={<AddDevice />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
