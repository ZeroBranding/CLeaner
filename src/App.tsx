import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';

// Pages
import Dashboard from '@pages/Dashboard';
import SystemScan from '@pages/SystemScan';
import Cleaning from '@pages/Cleaning';
import AIAssistant from '@pages/AIAssistant';
import Settings from '@pages/Settings';
import SystemInfo from '@pages/SystemInfo';

// Components
import Layout from '@components/Layout';
import LoadingScreen from '@components/LoadingScreen';
import ErrorBoundary from '@components/ErrorBoundary';

// Stores & Hooks
import { useSystemStore } from '@store/systemStore';
import { useWebSocket } from '@hooks/useWebSocket';

// Styles
import './styles/globals.css';

// React Query Client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5000,
      retry: 1,
    },
  },
});

function App() {
  const { initialize, isInitialized } = useSystemStore();
  const { connect } = useWebSocket();

  useEffect(() => {
    // Initialisiere App
    initialize();
    
    // Verbinde WebSocket für Echtzeit-Updates
    connect('ws://localhost:8000/ws');
  }, []);

  if (!isInitialized) {
    return <LoadingScreen />;
  }

  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <Router>
          <Layout>
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/scan" element={<SystemScan />} />
              <Route path="/clean" element={<Cleaning />} />
              <Route path="/ai" element={<AIAssistant />} />
              <Route path="/system" element={<SystemInfo />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </Layout>
        </Router>
        <Toaster 
          position="bottom-right"
          toastOptions={{
            className: 'dark:bg-gray-800 dark:text-white',
            duration: 4000,
          }}
        />
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;