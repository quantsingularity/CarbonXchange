import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import Dashboard from './pages/Dashboard';
import MarketAnalysis from './pages/MarketAnalysis';
import CreditVisualization from './pages/CreditVisualization';

function App() {
  return (
    <Router>
      <MainLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/analysis" element={<MarketAnalysis />} />
          <Route path="/visualization" element={<CreditVisualization />} />
        </Routes>
      </MainLayout>
    </Router>
  );
}

export default App;
