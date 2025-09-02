import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles/globals.css';

// Verhindere Kontextmenü in Production
if (import.meta.env.PROD) {
  document.addEventListener('contextmenu', (e) => e.preventDefault());
}

// Dark Mode als Standard
if (!localStorage.getItem('theme')) {
  localStorage.setItem('theme', 'dark');
  document.documentElement.classList.add('dark');
}

// Performance Monitoring
if (import.meta.env.DEV) {
  const reportWebVitals = async () => {
    const { getCLS, getFID, getFCP, getLCP, getTTFB } = await import('web-vitals');
    getCLS(console.log);
    getFID(console.log);
    getFCP(console.log);
    getLCP(console.log);
    getTTFB(console.log);
  };
  reportWebVitals();
}

// React 18 Root
const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);