import { contextBridge, ipcRenderer } from 'electron'
import { electronAPI } from '@electron-toolkit/preload'

// Custom APIs for renderer
const api = {
  system: {
    analyze: () => ipcRenderer.invoke('system:analyze'),
    cleanup: (options: any) => ipcRenderer.invoke('system:cleanup', options),
    checkDrivers: () => ipcRenderer.invoke('system:check-drivers'),
    getSystemInfo: () => ipcRenderer.invoke('system:get-info'),
    getPerformance: () => ipcRenderer.invoke('system:get-performance'),
    getStorage: () => ipcRenderer.invoke('system:get-storage'),
    getNetwork: () => ipcRenderer.invoke('system:get-network'),
    getProcesses: () => ipcRenderer.invoke('system:get-processes'),
    getServices: () => ipcRenderer.invoke('system:get-services'),
    getStartup: () => ipcRenderer.invoke('system:get-startup'),
    getUpdates: () => ipcRenderer.invoke('system:get-updates'),
    getSecurity: () => ipcRenderer.invoke('system:get-security'),
    getOptimization: () => ipcRenderer.invoke('system:get-optimization'),
    getRecommendations: () => ipcRenderer.invoke('system:get-recommendations')
  },
  cleanup: {
    gpu: () => ipcRenderer.invoke('cleanup:gpu'),
    cpu: () => ipcRenderer.invoke('cleanup:cpu'),
    ssd: () => ipcRenderer.invoke('cleanup:ssd'),
    ram: () => ipcRenderer.invoke('cleanup:ram'),
    browser: (browser: string) => ipcRenderer.invoke('cleanup:browser', browser),
    system: () => ipcRenderer.invoke('cleanup:system'),
    temp: () => ipcRenderer.invoke('cleanup:temp'),
    logs: () => ipcRenderer.invoke('cleanup:logs'),
    downloads: () => ipcRenderer.invoke('cleanup:downloads'),
    recycle: () => ipcRenderer.invoke('cleanup:recycle'),
    registry: () => ipcRenderer.invoke('cleanup:registry'),
    dns: () => ipcRenderer.invoke('cleanup:dns'),
    network: () => ipcRenderer.invoke('cleanup:network'),
    fonts: () => ipcRenderer.invoke('cleanup:fonts'),
    cache: () => ipcRenderer.invoke('cleanup:cache')
  },
  drivers: {
    check: () => ipcRenderer.invoke('drivers:check'),
    update: (driver: any) => ipcRenderer.invoke('drivers:update', driver),
    backup: (driver: any) => ipcRenderer.invoke('drivers:backup', driver),
    restore: (driver: any) => ipcRenderer.invoke('drivers:restore', driver),
    uninstall: (driver: any) => ipcRenderer.invoke('drivers:uninstall', driver),
    download: (driver: any) => ipcRenderer.invoke('drivers:download', driver),
    install: (driver: any) => ipcRenderer.invoke('drivers:install', driver),
    scan: () => ipcRenderer.invoke('drivers:scan'),
    getInstalled: () => ipcRenderer.invoke('drivers:get-installed'),
    getAvailable: () => ipcRenderer.invoke('drivers:get-available'),
    getCompatible: () => ipcRenderer.invoke('drivers:get-compatible')
  },
  chat: {
    send: (message: string) => ipcRenderer.invoke('chat:send', message),
    getHistory: () => ipcRenderer.invoke('chat:get-history'),
    clearHistory: () => ipcRenderer.invoke('chat:clear-history'),
    getSuggestions: () => ipcRenderer.invoke('chat:get-suggestions'),
    analyze: (query: string) => ipcRenderer.invoke('chat:analyze', query),
    optimize: (suggestion: string) => ipcRenderer.invoke('chat:optimize', suggestion)
  },
  settings: {
    get: () => ipcRenderer.invoke('settings:get'),
    set: (key: string, value: any) => ipcRenderer.invoke('settings:set', key, value),
    reset: () => ipcRenderer.invoke('settings:reset'),
    export: () => ipcRenderer.invoke('settings:export'),
    import: (data: any) => ipcRenderer.invoke('settings:import', data),
    getDefaults: () => ipcRenderer.invoke('settings:get-defaults'),
    validate: (settings: any) => ipcRenderer.invoke('settings:validate', settings)
  },
  dialog: {
    showError: (title: string, content: string) => ipcRenderer.invoke('dialog:show-error', title, content),
    showMessage: (options: any) => ipcRenderer.invoke('dialog:show-message', options),
    showOpenDialog: (options: any) => ipcRenderer.invoke('dialog:show-open', options),
    showSaveDialog: (options: any) => ipcRenderer.invoke('dialog:show-save', options),
    showConfirm: (options: any) => ipcRenderer.invoke('dialog:show-confirm', options)
  },
  file: {
    read: (path: string) => ipcRenderer.invoke('file:read', path),
    write: (path: string, data: any) => ipcRenderer.invoke('file:write', path, data),
    delete: (path: string) => ipcRenderer.invoke('file:delete', path),
    exists: (path: string) => ipcRenderer.invoke('file:exists', path),
    getSize: (path: string) => ipcRenderer.invoke('file:get-size', path),
    getModified: (path: string) => ipcRenderer.invoke('file:get-modified', path),
    copy: (src: string, dest: string) => ipcRenderer.invoke('file:copy', src, dest),
    move: (src: string, dest: string) => ipcRenderer.invoke('file:move', src, dest),
    list: (path: string) => ipcRenderer.invoke('file:list', path),
    createDir: (path: string) => ipcRenderer.invoke('file:create-dir', path)
  },
  process: {
    execute: (command: string, args: string[]) => ipcRenderer.invoke('process:execute', command, args),
    kill: (pid: number) => ipcRenderer.invoke('process:kill', pid),
    getList: () => ipcRenderer.invoke('process:get-list'),
    getInfo: (pid: number) => ipcRenderer.invoke('process:get-info', pid),
    getUsage: (pid: number) => ipcRenderer.invoke('process:get-usage', pid),
    setPriority: (pid: number, priority: string) => ipcRenderer.invoke('process:set-priority', pid, priority)
  },
  network: {
    test: () => ipcRenderer.invoke('network:test'),
    getInfo: () => ipcRenderer.invoke('network:get-info'),
    getConnections: () => ipcRenderer.invoke('network:get-connections'),
    getInterfaces: () => ipcRenderer.invoke('network:get-interfaces'),
    ping: (host: string) => ipcRenderer.invoke('network:ping', host),
    traceroute: (host: string) => ipcRenderer.invoke('network:traceroute', host),
    speedTest: () => ipcRenderer.invoke('network:speed-test'),
    flushDNS: () => ipcRenderer.invoke('network:flush-dns'),
    resetNetwork: () => ipcRenderer.invoke('network:reset')
  },
  security: {
    scan: () => ipcRenderer.invoke('security:scan'),
    getThreats: () => ipcRenderer.invoke('security:get-threats'),
    quarantine: (file: string) => ipcRenderer.invoke('security:quarantine', file),
    remove: (file: string) => ipcRenderer.invoke('security:remove', file),
    getFirewall: () => ipcRenderer.invoke('security:get-firewall'),
    setFirewall: (enabled: boolean) => ipcRenderer.invoke('security:set-firewall', enabled),
    getUpdates: () => ipcRenderer.invoke('security:get-updates'),
    installUpdates: () => ipcRenderer.invoke('security:install-updates'),
    getVulnerabilities: () => ipcRenderer.invoke('security:get-vulnerabilities'),
    fixVulnerabilities: () => ipcRenderer.invoke('security:fix-vulnerabilities')
  },
  optimization: {
    analyze: () => ipcRenderer.invoke('optimization:analyze'),
    optimize: (type: string) => ipcRenderer.invoke('optimization:optimize', type),
    getRecommendations: () => ipcRenderer.invoke('optimization:get-recommendations'),
    applyRecommendations: (recommendations: string[]) => ipcRenderer.invoke('optimization:apply', recommendations),
    getPerformance: () => ipcRenderer.invoke('optimization:get-performance'),
    benchmark: () => ipcRenderer.invoke('optimization:benchmark'),
    defrag: (drive: string) => ipcRenderer.invoke('optimization:defrag', drive),
    trim: (drive: string) => ipcRenderer.invoke('optimization:trim', drive),
    compress: (path: string) => ipcRenderer.invoke('optimization:compress', path),
    decompress: (path: string) => ipcRenderer.invoke('optimization:decompress', path)
  },
  monitoring: {
    start: () => ipcRenderer.invoke('monitoring:start'),
    stop: () => ipcRenderer.invoke('monitoring:stop'),
    getData: () => ipcRenderer.invoke('monitoring:get-data'),
    getAlerts: () => ipcRenderer.invoke('monitoring:get-alerts'),
    setThresholds: (thresholds: any) => ipcRenderer.invoke('monitoring:set-thresholds', thresholds),
    getReports: () => ipcRenderer.invoke('monitoring:get-reports'),
    exportReport: (format: string) => ipcRenderer.invoke('monitoring:export-report', format),
    scheduleReport: (schedule: any) => ipcRenderer.invoke('monitoring:schedule-report', schedule)
  },
  backup: {
    create: (options: any) => ipcRenderer.invoke('backup:create', options),
    restore: (backup: string) => ipcRenderer.invoke('backup:restore', backup),
    list: () => ipcRenderer.invoke('backup:list'),
    delete: (backup: string) => ipcRenderer.invoke('backup:delete', backup),
    verify: (backup: string) => ipcRenderer.invoke('backup:verify', backup),
    schedule: (schedule: any) => ipcRenderer.invoke('backup:schedule', schedule),
    getStatus: () => ipcRenderer.invoke('backup:get-status'),
    cancel: () => ipcRenderer.invoke('backup:cancel')
  },
  scheduler: {
    add: (task: any) => ipcRenderer.invoke('scheduler:add', task),
    remove: (id: string) => ipcRenderer.invoke('scheduler:remove', id),
    list: () => ipcRenderer.invoke('scheduler:list'),
    enable: (id: string) => ipcRenderer.invoke('scheduler:enable', id),
    disable: (id: string) => ipcRenderer.invoke('scheduler:disable', id),
    run: (id: string) => ipcRenderer.invoke('scheduler:run', id),
    getNext: () => ipcRenderer.invoke('scheduler:get-next'),
    getHistory: () => ipcRenderer.invoke('scheduler:get-history')
  }
}

// Use `contextBridge` APIs to expose Electron APIs to
// renderer only if context isolation is enabled, otherwise
// just add to the DOM global.
if (process.contextIsolated) {
  try {
    contextBridge.exposeInMainWorld('electron', electronAPI)
    contextBridge.exposeInMainWorld('api', api)
  } catch (error) {
    console.error(error)
  }
} else {
  // @ts-ignore (define in dts)
  window.electron = electronAPI
  // @ts-ignore (define in dts)
  window.api = api
}
