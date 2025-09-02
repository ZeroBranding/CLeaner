import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  MagnifyingGlassIcon,
  PlayIcon,
  StopIcon,
  DocumentIcon,
  FolderIcon,
  TrashIcon,
  CheckIcon,
  XMarkIcon,
  ClockIcon,
  ServerIcon,
  CpuChipIcon,
  PhotoIcon,
  VideoCameraIcon,
  MusicalNoteIcon,
  DocumentTextIcon,
  ArchiveBoxIcon
} from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';

// Store & Hooks
import { 
  useSystemStore, 
  useIsScanning, 
  useCurrentScan, 
  useSelectedItems 
} from '@store/systemStore';
import { useWebSocket } from '@hooks/useWebSocket';

// Utils
import { formatBytes, formatDate } from '@utils/format';

interface ScanCategory {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  enabled: boolean;
  estimatedFiles?: number;
  estimatedSize?: string;
}

const SystemScan: React.FC = () => {
  const { 
    startScan, 
    stopScan, 
    selectItem, 
    deselectItem, 
    selectAll, 
    deselectAll 
  } = useSystemStore();
  
  const isScanning = useIsScanning();
  const currentScan = useCurrentScan();
  const selectedItems = useSelectedItems();
  const { connect, isConnected } = useWebSocket();

  const [scanProgress, setScanProgress] = useState(0);
  const [currentFile, setCurrentFile] = useState('');
  const [categories, setCategories] = useState<ScanCategory[]>([
    {
      id: 'temp_files',
      name: 'Temporäre Dateien',
      description: 'Windows Temp, Browser Cache, Logs',
      icon: <DocumentIcon className="w-5 h-5" />,
      enabled: true,
      estimatedFiles: 1250,
      estimatedSize: '2.3 GB'
    },
    {
      id: 'system_cache',
      name: 'System-Cache',
      description: 'DNS Cache, Prefetch, System Temporary',
      icon: <ServerIcon className="w-5 h-5" />,
      enabled: true,
      estimatedFiles: 890,
      estimatedSize: '1.8 GB'
    },
    {
      id: 'browser_data',
      name: 'Browser-Daten',
      description: 'Cache, Cookies, Verlauf, Downloads',
      icon: <FolderIcon className="w-5 h-5" />,
      enabled: false,
      estimatedFiles: 2100,
      estimatedSize: '4.1 GB'
    },
    {
      id: 'duplicate_files',
      name: 'Doppelte Dateien',
      description: 'Identische Dateien auf verschiedenen Pfaden',
      icon: <DocumentTextIcon className="w-5 h-5" />,
      enabled: true,
      estimatedFiles: 340,
      estimatedSize: '850 MB'
    },
    {
      id: 'large_files',
      name: 'Große Dateien',
      description: 'Dateien über 100MB',
      icon: <ArchiveBoxIcon className="w-5 h-5" />,
      enabled: false,
      estimatedFiles: 45,
      estimatedSize: '12.4 GB'
    },
    {
      id: 'old_downloads',
      name: 'Alte Downloads',
      description: 'Downloads älter als 30 Tage',
      icon: <PhotoIcon className="w-5 h-5" />,
      enabled: false,
      estimatedFiles: 180,
      estimatedSize: '3.2 GB'
    }
  ]);

  useEffect(() => {
    // Verbinde WebSocket für Live-Updates
    connect('ws://localhost:8000/ws');
  }, [connect]);

  // Simuliere Scan-Progress (wird normalerweise via WebSocket empfangen)
  useEffect(() => {
    if (isScanning) {
      const interval = setInterval(() => {
        setScanProgress(prev => {
          const newProgress = prev + Math.random() * 5;
          if (newProgress >= 100) {
            clearInterval(interval);
            return 100;
          }
          return newProgress;
        });
        
        // Simuliere aktuellen Datei-Namen
        const sampleFiles = [
          'C:\\Windows\\Temp\\temp_file_123.tmp',
          'C:\\Users\\User\\AppData\\Local\\cache.dat',
          'C:\\Program Files\\App\\logs\\error.log',
          'C:\\Windows\\Prefetch\\app.exe.pf'
        ];
        setCurrentFile(sampleFiles[Math.floor(Math.random() * sampleFiles.length)]);
      }, 800);

      return () => clearInterval(interval);
    } else {
      setScanProgress(0);
      setCurrentFile('');
    }
  }, [isScanning]);

  const handleCategoryToggle = (categoryId: string) => {
    setCategories(prev => prev.map(cat => 
      cat.id === categoryId ? { ...cat, enabled: !cat.enabled } : cat
    ));
  };

  const handleStartScan = async () => {
    const enabledCategories = categories
      .filter(cat => cat.enabled)
      .map(cat => cat.id);

    if (enabledCategories.length === 0) {
      toast.error('Bitte wählen Sie mindestens eine Kategorie aus');
      return;
    }

    try {
      await startScan(enabledCategories);
      toast.success('System-Scan gestartet');
    } catch (error) {
      toast.error('Fehler beim Starten des Scans');
      console.error(error);
    }
  };

  const handleStopScan = () => {
    stopScan();
    toast.info('Scan wurde gestoppt');
  };

  const handleSelectAll = () => {
    selectAll();
    toast.success('Alle Elemente ausgewählt');
  };

  const handleDeselectAll = () => {
    deselectAll();
    toast.info('Auswahl aufgehoben');
  };

  const renderFileList = () => {
    if (!currentScan?.categories) return null;

    const allFiles: any[] = [];
    Object.entries(currentScan.categories).forEach(([categoryName, category]: [string, any]) => {
      if (category.items) {
        category.items.forEach((item: any) => {
          allFiles.push({
            ...item,
            category: categoryName
          });
        });
      }
    });

    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-white">
            Gefundene Dateien ({allFiles.length})
          </h3>
          <div className="flex space-x-2">
            <button
              onClick={handleSelectAll}
              className="btn-glow px-4 py-2 bg-primary-500/20 text-primary-400 border border-primary-500/30 rounded-lg hover:bg-primary-500/30 transition-all"
            >
              Alle auswählen
            </button>
            <button
              onClick={handleDeselectAll}
              className="px-4 py-2 bg-gray-500/20 text-gray-400 border border-gray-500/30 rounded-lg hover:bg-gray-500/30 transition-all"
            >
              Auswahl aufheben
            </button>
          </div>
        </div>

        <div className="glass-card max-h-96 overflow-y-auto custom-scrollbar">
          <div className="space-y-2 p-4">
            {allFiles.map((file, index) => (
              <motion.div
                key={`${file.path}-${index}`}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.02 }}
                className={`flex items-center space-x-3 p-3 rounded-lg cursor-pointer transition-all ${
                  selectedItems.includes(file.path)
                    ? 'bg-primary-500/20 border border-primary-500/50'
                    : 'bg-white/5 hover:bg-white/10 border border-white/10'
                }`}
                onClick={() => {
                  if (selectedItems.includes(file.path)) {
                    deselectItem(file.path);
                  } else {
                    selectItem(file.path);
                  }
                }}
              >
                <div className={`w-5 h-5 rounded border-2 flex items-center justify-center ${
                  selectedItems.includes(file.path)
                    ? 'bg-primary-500 border-primary-500'
                    : 'border-gray-400'
                }`}>
                  {selectedItems.includes(file.path) && (
                    <CheckIcon className="w-3 h-3 text-white" />
                  )}
                </div>
                
                <DocumentIcon className="w-4 h-4 text-gray-400" />
                
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-white truncate">{file.name || file.path.split('/').pop()}</p>
                  <p className="text-xs text-gray-400 truncate">{file.path}</p>
                </div>
                
                <div className="text-right">
                  <p className="text-sm text-gray-300">{formatBytes(file.size || 0)}</p>
                  <p className="text-xs text-gray-500">{file.category}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-8 p-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <h1 className="text-4xl font-bold text-gradient mb-4">System Scanner</h1>
        <p className="text-gray-400 text-lg">
          Scannen Sie Ihr System nach unnötigen Dateien und Optimierungsmöglichkeiten
        </p>
        
        {isConnected && (
          <div className="inline-flex items-center space-x-2 mt-4 px-4 py-2 bg-green-500/20 border border-green-500/30 rounded-full">
            <div className="pulse-dot w-2 h-2"></div>
            <span className="text-green-400 text-sm">Live-Updates aktiv</span>
          </div>
        )}
      </motion.div>

      {/* Kategorie-Auswahl */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="glass-card p-6"
      >
        <h2 className="text-xl font-semibold text-white mb-6 flex items-center">
          <MagnifyingGlassIcon className="w-5 h-5 mr-2 text-primary-400" />
          Scan-Kategorien
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {categories.map((category) => (
            <motion.div
              key={category.id}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className={`p-4 rounded-lg border cursor-pointer transition-all ${
                category.enabled
                  ? 'bg-primary-500/20 border-primary-500/50 shadow-lg shadow-primary-500/20'
                  : 'bg-white/5 border-white/10 hover:border-white/20'
              }`}
              onClick={() => handleCategoryToggle(category.id)}
            >
              <div className="flex items-start space-x-3">
                <div className={`w-6 h-6 rounded border-2 flex items-center justify-center mt-1 ${
                  category.enabled
                    ? 'bg-primary-500 border-primary-500'
                    : 'border-gray-400'
                }`}>
                  {category.enabled && (
                    <CheckIcon className="w-4 h-4 text-white" />
                  )}
                </div>
                
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    {category.icon}
                    <h3 className="font-semibold text-white">{category.name}</h3>
                  </div>
                  
                  <p className="text-sm text-gray-400 mb-3">{category.description}</p>
                  
                  {category.estimatedFiles && (
                    <div className="text-xs text-gray-500 space-y-1">
                      <div>≈ {category.estimatedFiles.toLocaleString()} Dateien</div>
                      <div>≈ {category.estimatedSize}</div>
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        <div className="mt-6 flex items-center justify-between">
          <div className="text-sm text-gray-400">
            {categories.filter(c => c.enabled).length} von {categories.length} Kategorien ausgewählt
          </div>
          
          <div className="flex space-x-3">
            <button
              onClick={() => setCategories(prev => prev.map(cat => ({ ...cat, enabled: true })))}
              className="text-sm text-primary-400 hover:text-primary-300 transition-colors"
            >
              Alle auswählen
            </button>
            <button
              onClick={() => setCategories(prev => prev.map(cat => ({ ...cat, enabled: false })))}
              className="text-sm text-gray-400 hover:text-gray-300 transition-colors"
            >
              Alle abwählen
            </button>
          </div>
        </div>
      </motion.div>

      {/* Scan Controls & Progress */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="glass-card p-6"
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-white flex items-center">
            <CpuChipIcon className="w-5 h-5 mr-2 text-primary-400" />
            Scan-Kontrolle
          </h2>
          
          <div className="flex space-x-3">
            {!isScanning ? (
              <button
                onClick={handleStartScan}
                disabled={categories.filter(c => c.enabled).length === 0}
                className="btn-glow px-6 py-3 bg-primary-500/20 text-primary-400 border border-primary-500/30 rounded-lg hover:bg-primary-500/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                <PlayIcon className="w-4 h-4" />
                <span>Scan starten</span>
              </button>
            ) : (
              <button
                onClick={handleStopScan}
                className="px-6 py-3 bg-red-500/20 text-red-400 border border-red-500/30 rounded-lg hover:bg-red-500/30 transition-all flex items-center space-x-2"
              >
                <StopIcon className="w-4 h-4" />
                <span>Scan stoppen</span>
              </button>
            )}
          </div>
        </div>

        {/* Progress Bar */}
        <AnimatePresence>
          {isScanning && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="space-y-4"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-300">Scan-Fortschritt</span>
                  <span className="text-sm text-primary-400">{Math.round(scanProgress)}%</span>
                </div>
                
                <div className="w-full bg-gray-700 rounded-full h-3 overflow-hidden">
                  <motion.div
                    className="h-full bg-gradient-to-r from-primary-500 to-secondary-500 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${scanProgress}%` }}
                    transition={{ duration: 0.5 }}
                  />
                </div>
              </div>

              {/* Current File */}
              <div className="flex items-center space-x-3 p-3 bg-white/5 rounded-lg">
                <div className="spinner w-5 h-5"></div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-300">Scanne gerade:</p>
                  <p className="text-xs text-gray-400 truncate font-mono">{currentFile}</p>
                </div>
              </div>

              {/* Scan Stats */}
              <div className="grid grid-cols-3 gap-4 text-center">
                <div className="bg-white/5 rounded-lg p-3">
                  <div className="text-lg font-bold text-primary-400">
                    {Math.floor(scanProgress * 23).toLocaleString()}
                  </div>
                  <div className="text-xs text-gray-400">Dateien gescannt</div>
                </div>
                <div className="bg-white/5 rounded-lg p-3">
                  <div className="text-lg font-bold text-secondary-400">
                    {Math.floor(scanProgress * 0.8).toLocaleString()} MB
                  </div>
                  <div className="text-xs text-gray-400">Gefunden</div>
                </div>
                <div className="bg-white/5 rounded-lg p-3">
                  <div className="text-lg font-bold text-green-400">
                    <ClockIcon className="w-4 h-4 inline mr-1" />
                    {Math.floor((100 - scanProgress) * 2)}s
                  </div>
                  <div className="text-xs text-gray-400">Verbleibend</div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>

      {/* Scan Results */}
      <AnimatePresence>
        {currentScan && !isScanning && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="glass-card p-6"
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-white flex items-center">
                <CheckIcon className="w-5 h-5 mr-2 text-green-400" />
                Scan-Ergebnisse
              </h2>
              
              <div className="text-sm text-gray-400">
                Abgeschlossen: {formatDate(currentScan.timestamp)}
              </div>
            </div>

            {/* Results Summary */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="bg-gradient-to-r from-primary-500/20 to-secondary-500/20 rounded-lg p-4 border border-primary-500/30">
                <div className="text-2xl font-bold text-primary-400">
                  {currentScan.total_files?.toLocaleString() || '0'}
                </div>
                <div className="text-sm text-gray-300">Dateien gefunden</div>
              </div>
              
              <div className="bg-gradient-to-r from-secondary-500/20 to-accent-red/20 rounded-lg p-4 border border-secondary-500/30">
                <div className="text-2xl font-bold text-secondary-400">
                  {formatBytes(currentScan.total_size || 0)}
                </div>
                <div className="text-sm text-gray-300">Gesamtgröße</div>
              </div>
              
              <div className="bg-gradient-to-r from-green-500/20 to-primary-500/20 rounded-lg p-4 border border-green-500/30">
                <div className="text-2xl font-bold text-green-400">
                  {selectedItems.length.toLocaleString()}
                </div>
                <div className="text-sm text-gray-300">Ausgewählt</div>
              </div>
            </div>

            {/* File List */}
            {renderFileList()}

            {/* Action Buttons */}
            <div className="mt-6 flex justify-end space-x-3">
              <button
                onClick={() => window.location.href = '/clean'}
                disabled={selectedItems.length === 0}
                className="btn-glow px-6 py-3 bg-green-500/20 text-green-400 border border-green-500/30 rounded-lg hover:bg-green-500/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                <TrashIcon className="w-4 h-4" />
                <span>Bereinigung starten ({selectedItems.length})</span>
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Empty State */}
      {!currentScan && !isScanning && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="text-center py-12"
        >
          <MagnifyingGlassIcon className="w-16 h-16 text-gray-500 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-300 mb-2">
            Bereit für System-Scan
          </h3>
          <p className="text-gray-500">
            Wählen Sie Kategorien aus und starten Sie den Scan-Vorgang
          </p>
        </motion.div>
      )}
    </div>
  );
};

export default SystemScan;