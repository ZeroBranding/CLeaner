// Electron API Type Definitions

export interface ElectronAPI {
  // Window Controls
  minimizeWindow: () => void;
  maximizeWindow: () => void;
  closeWindow: () => void;
  onMaximized: (callback: () => void) => void;
  onUnmaximized: (callback: () => void) => void;
  
  // System Info
  getSystemInfo: () => Promise<SystemInfo>;
  isAdmin: () => Promise<boolean>;
  
  // File Operations
  showSaveDialog: (options: SaveDialogOptions) => Promise<SaveDialogResult>;
  showOpenDialog: (options: OpenDialogOptions) => Promise<OpenDialogResult>;
  
  // App Events
  onQuickScan: (callback: () => void) => void;
  onNewScan: (callback: () => void) => void;
  onOpenSettings: (callback: () => void) => void;
  
  // Settings
  setAutoLaunch: (enable: boolean) => void;
  
  // External Links
  openExternal: (url: string) => void;
  
  // Cleaning Operations
  performClean: (items: string[]) => Promise<CleanResult>;
  createBackup: (items: string[]) => Promise<string>;
  restoreBackup: (backupPath: string) => Promise<boolean>;
  
  // Scan Operations
  startSystemScan: (options: ScanOptions) => Promise<ScanResult>;
  stopSystemScan: () => void;
  getScanResults: (scanId: number) => Promise<ScanResult>;
  
  // AI Operations
  askAI: (prompt: string, context?: string) => Promise<AIResponse>;
  getAIModels: () => Promise<AIModel[]>;
  loadAIModel: (modelName: string) => Promise<boolean>;
  
  // Database Operations
  getScanHistory: (days: number) => Promise<ScanHistory[]>;
  getCleaningHistory: (days: number) => Promise<CleaningHistory[]>;
  clearHistory: () => Promise<boolean>;
  exportData: (filepath: string) => Promise<boolean>;
  importData: (filepath: string) => Promise<boolean>;
  
  // Performance Monitoring
  startMonitoring: () => void;
  stopMonitoring: () => void;
  getPerformanceMetrics: () => Promise<PerformanceMetrics>;
  
  // Updates
  checkForUpdates: () => Promise<UpdateInfo>;
  downloadUpdate: () => void;
  installUpdate: () => void;
  
  // Notifications
  showNotification: (title: string, body: string, icon?: string) => void;
  
  // Logging
  log: (level: LogLevel, message: string, data?: any) => void;
  
  // App Info
  getVersion: () => Promise<string>;
  getPlatform: () => string;
  getArch: () => string;
  
  // Cleanup
  removeAllListeners: (channel: string) => void;
}

// Type Definitions
export interface SystemInfo {
  platform: string;
  arch: string;
  version: string;
  totalmem: number;
  freemem: number;
  cpus: CPUInfo[];
}

export interface CPUInfo {
  model: string;
  speed: number;
  times: {
    user: number;
    nice: number;
    sys: number;
    idle: number;
    irq: number;
  };
}

export interface SaveDialogOptions {
  title?: string;
  defaultPath?: string;
  buttonLabel?: string;
  filters?: FileFilter[];
  properties?: SaveDialogProperty[];
}

export interface SaveDialogResult {
  canceled: boolean;
  filePath?: string;
}

export interface OpenDialogOptions {
  title?: string;
  defaultPath?: string;
  buttonLabel?: string;
  filters?: FileFilter[];
  properties?: OpenDialogProperty[];
}

export interface OpenDialogResult {
  canceled: boolean;
  filePaths: string[];
}

export interface FileFilter {
  name: string;
  extensions: string[];
}

export type SaveDialogProperty = 
  | 'showHiddenFiles'
  | 'createDirectory'
  | 'treatPackageAsDirectory'
  | 'showOverwriteConfirmation'
  | 'dontAddToRecent';

export type OpenDialogProperty = 
  | 'openFile'
  | 'openDirectory'
  | 'multiSelections'
  | 'showHiddenFiles'
  | 'createDirectory'
  | 'promptToCreate'
  | 'noResolveAliases'
  | 'treatPackageAsDirectory'
  | 'dontAddToRecent';

export interface CleanResult {
  success: boolean;
  filesDeleted: number;
  bytesFreed: number;
  errors: string[];
}

export interface ScanOptions {
  categories: string[];
  enableAI: boolean;
  deepScan: boolean;
}

export interface ScanResult {
  scanId: number;
  timestamp: string;
  totalFiles: number;
  totalSize: number;
  categories: Record<string, CategoryResult>;
}

export interface CategoryResult {
  name: string;
  count: number;
  size: number;
  items: ScanItem[];
}

export interface ScanItem {
  path: string;
  size: number;
  type: string;
  safetyScore: number;
  aiExplanation?: string;
}

export interface AIResponse {
  response: string;
  modelUsed: string;
  tokensUsed: number;
  responseTime: number;
}

export interface AIModel {
  name: string;
  provider: string;
  sizeGB: number;
  isAvailable: boolean;
  isLoaded: boolean;
}

export interface ScanHistory {
  id: number;
  timestamp: string;
  filesFound: number;
  sizeFound: number;
  filesCleaned: number;
  sizeFreed: number;
}

export interface CleaningHistory {
  id: number;
  scanId: number;
  timestamp: string;
  filesDeleted: number;
  sizeFreed: number;
  backupPath?: string;
}

export interface PerformanceMetrics {
  cpu: number;
  memory: number;
  disk: number;
  network: {
    sent: number;
    recv: number;
  };
  processes: number;
}

export interface UpdateInfo {
  available: boolean;
  version?: string;
  releaseNotes?: string;
  downloadUrl?: string;
}

export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

// Global declaration
declare global {
  interface Window {
    electronAPI: ElectronAPI;
  }
}