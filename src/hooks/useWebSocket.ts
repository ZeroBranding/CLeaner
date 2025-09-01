import { useEffect, useRef, useCallback, useState } from 'react';
import { io, Socket } from 'socket.io-client';
import toast from 'react-hot-toast';
import { useSystemStore } from '@store/systemStore';

interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
}

interface WebSocketHook {
  socket: Socket | null;
  isConnected: boolean;
  connect: (url: string) => void;
  disconnect: () => void;
  emit: (event: string, data: any) => void;
  on: (event: string, callback: (data: any) => void) => void;
  off: (event: string, callback?: (data: any) => void) => void;
}

export function useWebSocket(): WebSocketHook {
  const socketRef = useRef<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const { setScanResult, setSystemInfo } = useSystemStore();

  const connect = useCallback((url: string) => {
    if (socketRef.current?.connected) {
      console.log('WebSocket already connected');
      return;
    }

    console.log('Connecting to WebSocket:', url);
    
    socketRef.current = io(url, {
      transports: ['websocket'],
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
    });

    // Connection Events
    socketRef.current.on('connect', () => {
      console.log('✅ WebSocket connected');
      setIsConnected(true);
      toast.success('Verbindung zum Server hergestellt');
    });

    socketRef.current.on('disconnect', (reason) => {
      console.log('❌ WebSocket disconnected:', reason);
      setIsConnected(false);
      if (reason === 'io server disconnect') {
        toast.error('Verbindung vom Server getrennt');
      }
    });

    socketRef.current.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error);
      toast.error('Verbindungsfehler: ' + error.message);
    });

    // System Events
    socketRef.current.on('system_update', (data: any) => {
      handleSystemUpdate(data);
    });

    // Scan Events
    socketRef.current.on('scan_progress', (data: any) => {
      handleScanProgress(data);
    });

    socketRef.current.on('scan_complete', (data: any) => {
      handleScanComplete(data);
    });

    // Cleaning Events
    socketRef.current.on('cleaning_progress', (data: any) => {
      handleCleaningProgress(data);
    });

    socketRef.current.on('cleaning_complete', (data: any) => {
      handleCleaningComplete(data);
    });

    // Alert Events
    socketRef.current.on('system_alert', (data: any) => {
      handleSystemAlert(data);
    });
  }, []);

  const disconnect = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.disconnect();
      socketRef.current = null;
      setIsConnected(false);
    }
  }, []);

  const emit = useCallback((event: string, data: any) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit(event, data);
    } else {
      console.warn('WebSocket not connected, cannot emit:', event);
    }
  }, []);

  const on = useCallback((event: string, callback: (data: any) => void) => {
    if (socketRef.current) {
      socketRef.current.on(event, callback);
    }
  }, []);

  const off = useCallback((event: string, callback?: (data: any) => void) => {
    if (socketRef.current) {
      if (callback) {
        socketRef.current.off(event, callback);
      } else {
        socketRef.current.off(event);
      }
    }
  }, []);

  // Event Handlers
  const handleSystemUpdate = (data: any) => {
    // Update system store with real-time data
    if (data.cpu || data.memory || data.disk) {
      // Update charts and metrics
      window.dispatchEvent(new CustomEvent('system-metrics-update', { detail: data }));
    }
  };

  const handleScanProgress = (data: any) => {
    const { scan_id, status, progress } = data;
    
    // Update UI with scan progress
    window.dispatchEvent(new CustomEvent('scan-progress', { 
      detail: { scan_id, status, progress } 
    }));

    // Show toast for milestones
    if (progress === 0.25) {
      toast('Temporäre Dateien werden gescannt...', { icon: '🔍' });
    } else if (progress === 0.5) {
      toast('Cache-Dateien werden analysiert...', { icon: '📊' });
    } else if (progress === 0.75) {
      toast('Duplikate werden gesucht...', { icon: '🔎' });
    }
  };

  const handleScanComplete = (data: any) => {
    setScanResult(data);
    toast.success(`Scan abgeschlossen! ${data.total_files} Dateien gefunden.`);
    
    // Trigger UI update
    window.dispatchEvent(new CustomEvent('scan-complete', { detail: data }));
  };

  const handleCleaningProgress = (data: any) => {
    const { progress, current_file } = data;
    
    window.dispatchEvent(new CustomEvent('cleaning-progress', { 
      detail: { progress, current_file } 
    }));
  };

  const handleCleaningComplete = (data: any) => {
    const { files_deleted, bytes_freed } = data;
    const mb_freed = (bytes_freed / (1024 * 1024)).toFixed(2);
    
    toast.success(`Bereinigung abgeschlossen! ${files_deleted} Dateien gelöscht, ${mb_freed} MB freigegeben.`);
    
    window.dispatchEvent(new CustomEvent('cleaning-complete', { detail: data }));
  };

  const handleSystemAlert = (data: any) => {
    const { type, message, severity } = data;
    
    switch (severity) {
      case 'critical':
        toast.error(message, { duration: 10000 });
        break;
      case 'warning':
        toast(message, { icon: '⚠️', duration: 7000 });
        break;
      case 'info':
        toast(message, { icon: 'ℹ️' });
        break;
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    socket: socketRef.current,
    isConnected,
    connect,
    disconnect,
    emit,
    on,
    off,
  };
}

// Custom hook for scan progress
export function useScanProgress() {
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('');
  const [scanId, setScanId] = useState<number | null>(null);

  useEffect(() => {
    const handleProgress = (event: CustomEvent) => {
      const { scan_id, status: newStatus, progress: newProgress } = event.detail;
      setScanId(scan_id);
      setStatus(newStatus);
      setProgress(newProgress * 100);
    };

    window.addEventListener('scan-progress' as any, handleProgress);
    return () => window.removeEventListener('scan-progress' as any, handleProgress);
  }, []);

  return { scanId, status, progress };
}

// Custom hook for system metrics
export function useSystemMetrics() {
  const [metrics, setMetrics] = useState({
    cpu: 0,
    memory: 0,
    disk_io: 0,
    network: { sent: 0, recv: 0 },
    gpu: { usage: 0, memory: 0, temperature: 0 }
  });

  useEffect(() => {
    const handleUpdate = (event: CustomEvent) => {
      setMetrics(prev => ({ ...prev, ...event.detail }));
    };

    window.addEventListener('system-metrics-update' as any, handleUpdate);
    return () => window.removeEventListener('system-metrics-update' as any, handleUpdate);
  }, []);

  return metrics;
}