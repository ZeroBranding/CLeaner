import axios, { AxiosInstance, AxiosError } from 'axios';
import toast from 'react-hot-toast';

// API Base URL - kann über Umgebungsvariable konfiguriert werden
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Axios Instance erstellen
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor
api.interceptors.request.use(
  (config) => {
    // Token hinzufügen falls vorhanden (für Premium-Features)
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Log für Development
    if (import.meta.env.DEV) {
      console.log(`🚀 ${config.method?.toUpperCase()} ${config.url}`, config.data);
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response Interceptor
api.interceptors.response.use(
  (response) => {
    // Log für Development
    if (import.meta.env.DEV) {
      console.log(`✅ Response from ${response.config.url}:`, response.data);
    }
    return response;
  },
  (error: AxiosError) => {
    // Error Handling
    if (error.response) {
      // Server hat mit Fehlercode geantwortet
      const status = error.response.status;
      const message = (error.response.data as any)?.detail || error.message;
      
      switch (status) {
        case 400:
          toast.error(`Ungültige Anfrage: ${message}`);
          break;
        case 401:
          toast.error('Nicht autorisiert. Bitte melden Sie sich an.');
          // Redirect to login if needed
          break;
        case 403:
          toast.error('Zugriff verweigert. Premium-Feature?');
          break;
        case 404:
          toast.error('Ressource nicht gefunden');
          break;
        case 500:
          toast.error('Serverfehler. Bitte versuchen Sie es später erneut.');
          break;
        default:
          toast.error(`Fehler: ${message}`);
      }
    } else if (error.request) {
      // Anfrage wurde gesendet, aber keine Antwort erhalten
      toast.error('Keine Verbindung zum Server. Ist der API-Server gestartet?');
      console.error('No response received:', error.request);
    } else {
      // Fehler beim Erstellen der Anfrage
      toast.error('Anfragefehler: ' + error.message);
      console.error('Request setup error:', error.message);
    }
    
    return Promise.reject(error);
  }
);

// API Endpunkte
export const endpoints = {
  // System
  systemInfo: '/system/info',
  systemUsage: '/system/usage',
  systemProcesses: '/system/processes',
  
  // Scan
  scanStart: '/scan/start',
  scanStatus: (id: number) => `/scan/status/${id}`,
  scanResults: (id: number) => `/scan/results/${id}`,
  scanHistory: '/scan/history',
  
  // Cleaning
  cleanStart: '/clean/start',
  cleanHistory: '/clean/history',
  
  // AI
  aiChat: '/ai/chat',
  aiModels: '/ai/models',
  aiExplain: '/ai/explain',
  
  // Settings
  settingsGet: (userId: string) => `/settings/${userId}`,
  settingsUpdate: '/settings/update',
  
  // Health
  health: '/health',
  status: '/status',
};

// Helper functions
export const apiHelpers = {
  // System-Scan starten
  startScan: async (categories: string[], enableAI = true) => {
    return api.post(endpoints.scanStart, {
      categories,
      enable_ai: enableAI,
      user_id: 'default'
    });
  },
  
  // Scan-Status abfragen
  getScanStatus: async (scanId: number) => {
    return api.get(endpoints.scanStatus(scanId));
  },
  
  // Scan-Ergebnisse holen
  getScanResults: async (scanId: number) => {
    return api.get(endpoints.scanResults(scanId));
  },
  
  // Bereinigung starten
  startCleaning: async (scanId: number, selectedItems: string[], createBackup = true) => {
    return api.post(endpoints.cleanStart, {
      scan_id: scanId,
      selected_items: selectedItems,
      create_backup: createBackup,
      user_id: 'default'
    });
  },
  
  // AI-Chat
  sendAIMessage: async (prompt: string, context?: string) => {
    return api.post(endpoints.aiChat, {
      prompt,
      context,
      max_tokens: 500,
      temperature: 0.7
    });
  },
  
  // System-Info
  getSystemInfo: async () => {
    return api.get(endpoints.systemInfo);
  },
  
  // System-Auslastung
  getSystemUsage: async () => {
    return api.get(endpoints.systemUsage);
  },
  
  // Top-Prozesse
  getTopProcesses: async (sortBy = 'cpu', limit = 10) => {
    return api.get(endpoints.systemProcesses, {
      params: { sort_by: sortBy, limit }
    });
  },
  
  // Einstellungen
  getSettings: async (userId = 'default') => {
    return api.get(endpoints.settingsGet(userId));
  },
  
  updateSettings: async (settings: any) => {
    return api.post(endpoints.settingsUpdate, {
      user_id: 'default',
      ...settings
    });
  },
};

export default api;