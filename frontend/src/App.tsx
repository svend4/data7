import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { HomePage } from './pages/HomePage'
import { MonitoringDashboard } from './pages/MonitoringDashboard'
import './styles/global.css'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/monitoring" element={<MonitoringDashboard />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
