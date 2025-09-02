const { app, BrowserWindow, ipcMain, Menu, Tray, shell, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const isDev = process.env.NODE_ENV === 'development';

let mainWindow;
let apiProcess;
let tray;

// Python API Server starten
function startAPIServer() {
  const pythonExecutable = process.platform === 'win32' ? 'python' : 'python3';
  
  apiProcess = spawn(pythonExecutable, ['api_server.py'], {
    cwd: __dirname + '/..',
    stdio: 'inherit'
  });

  apiProcess.on('error', (err) => {
    console.error('Failed to start API server:', err);
    dialog.showErrorBox('API Server Error', 'Failed to start the backend server. Please ensure Python is installed.');
  });

  apiProcess.on('exit', (code) => {
    if (code !== 0) {
      console.error(`API server exited with code ${code}`);
    }
  });
}

// Hauptfenster erstellen
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1024,
    minHeight: 768,
    icon: path.join(__dirname, '../assets/icon.png'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    frame: false, // Frameless window für modernes Design
    backgroundColor: '#0a0a0a',
    titleBarStyle: 'hidden',
    titleBarOverlay: {
      color: '#0a0a0a',
      symbolColor: '#ffffff',
      height: 32
    }
  });

  // Lade die App
  if (isDev) {
    mainWindow.loadURL('http://localhost:3000');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }

  // Window Events
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  mainWindow.on('maximize', () => {
    mainWindow.webContents.send('window-maximized');
  });

  mainWindow.on('unmaximize', () => {
    mainWindow.webContents.send('window-unmaximized');
  });
}

// System Tray erstellen
function createTray() {
  tray = new Tray(path.join(__dirname, '../assets/icon.png'));
  
  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Dashboard öffnen',
      click: () => {
        if (mainWindow) {
          mainWindow.show();
          mainWindow.focus();
        }
      }
    },
    {
      label: 'Quick Scan',
      click: () => {
        if (mainWindow) {
          mainWindow.webContents.send('quick-scan');
        }
      }
    },
    { type: 'separator' },
    {
      label: 'Einstellungen',
      click: () => {
        if (mainWindow) {
          mainWindow.webContents.send('open-settings');
        }
      }
    },
    { type: 'separator' },
    {
      label: 'Beenden',
      click: () => {
        app.quit();
      }
    }
  ]);

  tray.setToolTip('GermanCodeZero Cleaner');
  tray.setContextMenu(contextMenu);

  tray.on('double-click', () => {
    if (mainWindow) {
      mainWindow.show();
      mainWindow.focus();
    }
  });
}

// App Menu erstellen
function createMenu() {
  const template = [
    {
      label: 'Datei',
      submenu: [
        {
          label: 'Neuer Scan',
          accelerator: 'CmdOrCtrl+N',
          click: () => {
            mainWindow.webContents.send('new-scan');
          }
        },
        { type: 'separator' },
        {
          label: 'Beenden',
          accelerator: 'CmdOrCtrl+Q',
          click: () => {
            app.quit();
          }
        }
      ]
    },
    {
      label: 'Bearbeiten',
      submenu: [
        { role: 'undo', label: 'Rückgängig' },
        { role: 'redo', label: 'Wiederholen' },
        { type: 'separator' },
        { role: 'cut', label: 'Ausschneiden' },
        { role: 'copy', label: 'Kopieren' },
        { role: 'paste', label: 'Einfügen' }
      ]
    },
    {
      label: 'Ansicht',
      submenu: [
        { role: 'reload', label: 'Neu laden' },
        { role: 'forceReload', label: 'Erzwungen neu laden' },
        { role: 'toggleDevTools', label: 'Entwicklertools' },
        { type: 'separator' },
        { role: 'resetZoom', label: 'Zoom zurücksetzen' },
        { role: 'zoomIn', label: 'Vergrößern' },
        { role: 'zoomOut', label: 'Verkleinern' },
        { type: 'separator' },
        { role: 'togglefullscreen', label: 'Vollbild' }
      ]
    },
    {
      label: 'Hilfe',
      submenu: [
        {
          label: 'Dokumentation',
          click: async () => {
            await shell.openExternal('https://github.com/ZeroBranding/CLeaner#readme');
          }
        },
        {
          label: 'Über',
          click: () => {
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'Über GermanCodeZero Cleaner',
              message: 'GermanCodeZero Cleaner v1.0.0',
              detail: 'Eine moderne, KI-gestützte System-Reinigungs-Anwendung mit 3D-Interface.\n\n© 2025 GermanCodeZero',
              buttons: ['OK']
            });
          }
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

// IPC Handlers
function setupIPC() {
  // Window Controls
  ipcMain.on('window-minimize', () => {
    mainWindow.minimize();
  });

  ipcMain.on('window-maximize', () => {
    if (mainWindow.isMaximized()) {
      mainWindow.unmaximize();
    } else {
      mainWindow.maximize();
    }
  });

  ipcMain.on('window-close', () => {
    mainWindow.close();
  });

  // System Info
  ipcMain.handle('get-system-info', async () => {
    const os = require('os');
    return {
      platform: process.platform,
      arch: process.arch,
      version: os.release(),
      totalmem: os.totalmem(),
      freemem: os.freemem(),
      cpus: os.cpus()
    };
  });

  // File Operations
  ipcMain.handle('show-save-dialog', async (event, options) => {
    const result = await dialog.showSaveDialog(mainWindow, options);
    return result;
  });

  ipcMain.handle('show-open-dialog', async (event, options) => {
    const result = await dialog.showOpenDialog(mainWindow, options);
    return result;
  });

  // Admin Check
  ipcMain.handle('is-admin', () => {
    if (process.platform === 'win32') {
      try {
        require('child_process').execSync('net session', { stdio: 'ignore' });
        return true;
      } catch {
        return false;
      }
    }
    return process.geteuid ? process.geteuid() === 0 : false;
  });

  // Auto-Launch
  ipcMain.on('set-auto-launch', (event, enable) => {
    app.setLoginItemSettings({
      openAtLogin: enable,
      path: app.getPath('exe')
    });
  });

  // Open External
  ipcMain.on('open-external', (event, url) => {
    shell.openExternal(url);
  });
}

// App Events
app.whenReady().then(() => {
  startAPIServer();
  createWindow();
  createTray();
  createMenu();
  setupIPC();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  // API Server beenden
  if (apiProcess) {
    apiProcess.kill();
  }
});

// Verhindere mehrere Instanzen
const gotTheLock = app.requestSingleInstanceLock();

if (!gotTheLock) {
  app.quit();
} else {
  app.on('second-instance', () => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
  });
}

// Crash Reporter
require('electron').crashReporter.start({
  submitURL: 'https://your-crash-report-server.com',
  productName: 'GermanCodeZero Cleaner',
  uploadToServer: false // Für Development deaktiviert
});