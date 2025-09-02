import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import api from '@api/client';

interface SystemInfo {
  os: string;
  cpu: {
    model: string;
    cores: number;
    threads: number;
    frequency: number;
    usage: number;
  };
  memory: {
    total: number;
    available: number;
    usage: number;
  };
  disk: Array<{
    device: string;
    total: number;
    free: number;
    percent: number;
  }>;
  gpu?: {
    name: string;
    memory: number;
    usage: number;
  };
}

interface ScanResult {
  scan_id: number;
  status: string;
  total_files: number;
  total_size: number;
  categories: Record<string, any>;
  timestamp: string;
}

interface SystemState {
  // State
  isInitialized: boolean;
  isScanning: boolean;
  isCleaning: boolean;
  systemInfo: SystemInfo | null;
  currentScan: ScanResult | null;
  scanHistory: ScanResult[];
  selectedItems: string[];
  
  // Settings
  theme: 'dark' | 'light';
  language: 'de' | 'en';
  autoScan: boolean;
  dataSharing: boolean;
  
  // Actions
  initialize: () => Promise<void>;
  setSystemInfo: (info: SystemInfo) => void;
  startScan: (categories: string[]) => Promise<void>;
  stopScan: () => void;
  setScanResult: (result: ScanResult) => void;
  selectItem: (path: string) => void;
  deselectItem: (path: string) => void;
  selectAll: () => void;
  deselectAll: () => void;
  startCleaning: () => Promise<void>;
  updateSettings: (settings: Partial<SystemState>) => void;
  reset: () => void;
}

const initialState = {
  isInitialized: false,
  isScanning: false,
  isCleaning: false,
  systemInfo: null,
  currentScan: null,
  scanHistory: [],
  selectedItems: [],
  theme: 'dark' as const,
  language: 'de' as const,
  autoScan: true,
  dataSharing: false,
};

export const useSystemStore = create<SystemState>()(
  devtools(
    persist(
      (set, get) => ({
        ...initialState,

        initialize: async () => {
          try {
            // Lade System-Info
            const response = await api.get('/system/info');
            set({ 
              systemInfo: response.data,
              isInitialized: true 
            });

            // Lade Scan-Historie
            const historyResponse = await api.get('/scan/history');
            set({ scanHistory: historyResponse.data.scans || [] });

            // Lade Einstellungen
            const settingsResponse = await api.get('/settings/default');
            set({
              autoScan: settingsResponse.data.auto_scan_enabled,
              dataSharing: settingsResponse.data.data_sharing_enabled,
              theme: settingsResponse.data.theme || 'dark',
              language: settingsResponse.data.language || 'de',
            });
          } catch (error) {
            console.error('Initialization failed:', error);
            set({ isInitialized: true }); // Trotzdem als initialisiert markieren
          }
        },

        setSystemInfo: (info) => set({ systemInfo: info }),

        startScan: async (categories) => {
          set({ isScanning: true });
          
          try {
            const response = await api.post('/scan/start', {
              categories,
              enable_ai: true,
              user_id: 'default'
            });
            
            const scanId = response.data.scan_id;
            
            // Polling für Scan-Status
            const pollInterval = setInterval(async () => {
              const statusResponse = await api.get(`/scan/status/${scanId}`);
              
              if (statusResponse.data.status === 'completed') {
                clearInterval(pollInterval);
                
                // Hole Ergebnisse
                const resultsResponse = await api.get(`/scan/results/${scanId}`);
                const scanResult = {
                  scan_id: scanId,
                  ...resultsResponse.data,
                  timestamp: new Date().toISOString()
                };
                
                set({
                  currentScan: scanResult,
                  isScanning: false,
                  scanHistory: [...get().scanHistory, scanResult]
                });
              } else if (statusResponse.data.status === 'failed') {
                clearInterval(pollInterval);
                set({ isScanning: false });
                throw new Error('Scan failed');
              }
            }, 1000);
            
          } catch (error) {
            set({ isScanning: false });
            throw error;
          }
        },

        stopScan: () => set({ isScanning: false }),

        setScanResult: (result) => set({ 
          currentScan: result,
          scanHistory: [...get().scanHistory, result]
        }),

        selectItem: (path) => set((state) => ({
          selectedItems: [...state.selectedItems, path]
        })),

        deselectItem: (path) => set((state) => ({
          selectedItems: state.selectedItems.filter(item => item !== path)
        })),

        selectAll: () => {
          const { currentScan } = get();
          if (currentScan) {
            const allPaths: string[] = [];
            Object.values(currentScan.categories).forEach((category: any) => {
              if (category.items) {
                category.items.forEach((item: any) => {
                  allPaths.push(item.path);
                });
              }
            });
            set({ selectedItems: allPaths });
          }
        },

        deselectAll: () => set({ selectedItems: [] }),

        startCleaning: async () => {
          const { currentScan, selectedItems } = get();
          if (!currentScan || selectedItems.length === 0) return;
          
          set({ isCleaning: true });
          
          try {
            const response = await api.post('/clean/start', {
              scan_id: currentScan.scan_id,
              selected_items: selectedItems,
              create_backup: true,
              user_id: 'default'
            });
            
            set({ 
              isCleaning: false,
              selectedItems: [],
              currentScan: null
            });
            
            return response.data;
          } catch (error) {
            set({ isCleaning: false });
            throw error;
          }
        },

        updateSettings: (settings) => set(settings),

        reset: () => set(initialState),
      }),
      {
        name: 'system-store',
        partialize: (state) => ({
          theme: state.theme,
          language: state.language,
          autoScan: state.autoScan,
          dataSharing: state.dataSharing,
        }),
      }
    )
  )
);

// Selectors
export const useIsScanning = () => useSystemStore((state) => state.isScanning);
export const useIsCleaning = () => useSystemStore((state) => state.isCleaning);
export const useCurrentScan = () => useSystemStore((state) => state.currentScan);
export const useSelectedItems = () => useSystemStore((state) => state.selectedItems);
export const useSystemInfo = () => useSystemStore((state) => state.systemInfo);
export const useTheme = () => useSystemStore((state) => state.theme);