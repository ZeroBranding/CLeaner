import { useEffect, useRef, useCallback } from 'react';
import { useSystemStore } from '@store/systemStore';

interface WebSocketMessage {
  type: 'scan_progress' | 'scan_complete' | 'scan_error' | 'system_update';
  data: any;
}

export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const { setScanResult, stopScan } = useSystemStore();

  const connect = useCallback((url: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      wsRef.current = new WebSocket(url);

      wsRef.current.onopen = () => {
        console.log('WebSocket verbunden');
      };

      wsRef.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          
          switch (message.type) {
            case 'scan_progress':
              // Progress wird über Store-Polling gehandhabt
              break;
              
            case 'scan_complete':
              setScanResult(message.data);
              stopScan();
              break;
              
            case 'scan_error':
              console.error('Scan Fehler:', message.data);
              stopScan();
              break;
              
            case 'system_update':
              // System-Updates verarbeiten
              break;
              
            default:
              console.log('Unbekannter WebSocket Nachrichtentyp:', message.type);
          }
        } catch (error) {
          console.error('Fehler beim Verarbeiten der WebSocket Nachricht:', error);
        }
      };

      wsRef.current.onclose = () => {
        console.log('WebSocket Verbindung geschlossen');
        // Reconnect nach 3 Sekunden
        setTimeout(() => connect(url), 3000);
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket Fehler:', error);
      };
    } catch (error) {
      console.error('Fehler beim Erstellen der WebSocket Verbindung:', error);
    }
  }, [setScanResult, stopScan]);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  }, []);

  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    connect,
    disconnect,
    sendMessage,
    isConnected: wsRef.current?.readyState === WebSocket.OPEN
  };
}