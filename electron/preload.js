const { contextBridge, ipcRenderer } = require('electron');

// Expose protected APIs to the renderer process
contextBridge.exposeInMainWorld('electronAPI', {
  // Window Controls
  minimizeWindow: () => ipcRenderer.send('window-minimize'),
  maximizeWindow: () => ipcRenderer.send('window-maximize'),
  closeWindow: () => ipcRenderer.send('window-close'),
  
  // Window State
  onMaximized: (callback) => ipcRenderer.on('window-maximized', callback),
  onUnmaximized: (callback) => ipcRenderer.on('window-unmaximized', callback),
  
  // System Info
  getSystemInfo: () => ipcRenderer.invoke('get-system-info'),
  isAdmin: () => ipcRenderer.invoke('is-admin'),
  
  // File Operations
  showSaveDialog: (options) => ipcRenderer.invoke('show-save-dialog', options),
  showOpenDialog: (options) => ipcRenderer.invoke('show-open-dialog', options),
  
  // App Events
  onQuickScan: (callback) => ipcRenderer.on('quick-scan', callback),
  onNewScan: (callback) => ipcRenderer.on('new-scan', callback),
  onOpenSettings: (callback) => ipcRenderer.on('open-settings', callback),
  
  // Settings
  setAutoLaunch: (enable) => ipcRenderer.send('set-auto-launch', enable),
  
  // External Links
  openExternal: (url) => ipcRenderer.send('open-external', url),
  
  // Cleaning Operations
  performClean: (items) => ipcRenderer.invoke('perform-clean', items),
  createBackup: (items) => ipcRenderer.invoke('create-backup', items),
  restoreBackup: (backupPath) => ipcRenderer.invoke('restore-backup', backupPath),
  
  // Scan Operations
  startSystemScan: (options) => ipcRenderer.invoke('start-system-scan', options),
  stopSystemScan: () => ipcRenderer.send('stop-system-scan'),
  getScanResults: (scanId) => ipcRenderer.invoke('get-scan-results', scanId),
  
  // AI Operations
  askAI: (prompt, context) => ipcRenderer.invoke('ask-ai', { prompt, context }),
  getAIModels: () => ipcRenderer.invoke('get-ai-models'),
  loadAIModel: (modelName) => ipcRenderer.invoke('load-ai-model', modelName),
  
  // Database Operations
  getScanHistory: (days) => ipcRenderer.invoke('get-scan-history', days),
  getCleaningHistory: (days) => ipcRenderer.invoke('get-cleaning-history', days),
  clearHistory: () => ipcRenderer.invoke('clear-history'),
  exportData: (filepath) => ipcRenderer.invoke('export-data', filepath),
  importData: (filepath) => ipcRenderer.invoke('import-data', filepath),
  
  // Performance Monitoring
  startMonitoring: () => ipcRenderer.send('start-monitoring'),
  stopMonitoring: () => ipcRenderer.send('stop-monitoring'),
  getPerformanceMetrics: () => ipcRenderer.invoke('get-performance-metrics'),
  
  // Updates
  checkForUpdates: () => ipcRenderer.invoke('check-for-updates'),
  downloadUpdate: () => ipcRenderer.send('download-update'),
  installUpdate: () => ipcRenderer.send('install-update'),
  
  // Notifications
  showNotification: (title, body, icon) => {
    ipcRenderer.send('show-notification', { title, body, icon });
  },
  
  // Logging
  log: (level, message, data) => {
    ipcRenderer.send('log', { level, message, data });
  },
  
  // App Info
  getVersion: () => ipcRenderer.invoke('get-app-version'),
  getPlatform: () => process.platform,
  getArch: () => process.arch,
  
  // Remove all listeners
  removeAllListeners: (channel) => {
    ipcRenderer.removeAllListeners(channel);
  }
});

// Security: Prevent window.opener attacks
window.opener = null;

// Log that preload script is loaded
console.log('Preload script loaded successfully');

// Handle context menu (right-click)
window.addEventListener('contextmenu', (e) => {
  e.preventDefault();
  ipcRenderer.send('show-context-menu', {
    x: e.clientX,
    y: e.clientY
  });
});

// Handle drag and drop
window.addEventListener('dragover', (e) => {
  e.preventDefault();
  e.stopPropagation();
});

window.addEventListener('drop', (e) => {
  e.preventDefault();
  e.stopPropagation();
  
  const files = Array.from(e.dataTransfer.files).map(file => file.path);
  if (files.length > 0) {
    ipcRenderer.send('files-dropped', files);
  }
});

// Performance observer
if (window.PerformanceObserver) {
  const observer = new PerformanceObserver((list) => {
    const entries = list.getEntries();
    entries.forEach((entry) => {
      if (entry.entryType === 'measure' || entry.entryType === 'navigation') {
        ipcRenderer.send('performance-metric', {
          name: entry.name,
          duration: entry.duration,
          startTime: entry.startTime
        });
      }
    });
  });
  
  observer.observe({ entryTypes: ['measure', 'navigation'] });
}