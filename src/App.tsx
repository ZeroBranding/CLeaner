import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { ThemeProvider } from './contexts/ThemeContext'
import { SystemProvider } from './contexts/SystemContext'
import Layout from './components/Layout/Layout'
import Dashboard from './pages/Dashboard'
import Chat from './pages/Chat'
import Cleanup from './pages/Cleanup'
import Drivers from './pages/Drivers'
import Settings from './pages/Settings'
import SystemInfo from './pages/SystemInfo'

function App() {
  return (
    <ThemeProvider>
      <SystemProvider>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/cleanup" element={<Cleanup />} />
            <Route path="/drivers" element={<Drivers />} />
            <Route path="/system" element={<SystemInfo />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </Layout>
      </SystemProvider>
    </ThemeProvider>
  )
}

export default App
