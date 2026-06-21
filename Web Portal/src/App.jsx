import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import Meets from './components/Meets';
import GenerateHeatSheet from './components/GenerateHeatSheet';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />}>
          <Route path="meets" element={<Meets />} />
          <Route path="generate" element={<GenerateHeatSheet />} />
          <Route path="rosters" element={<div className="animate-fade-in"><h2>Rosters</h2><p>Roster management coming soon...</p></div>} />
          <Route index element={<Navigate to="meets" replace />} />
        </Route>
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
