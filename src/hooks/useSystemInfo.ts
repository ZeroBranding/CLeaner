import { useQuery } from '@tanstack/react-query';
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
  network: Array<{
    interface: string;
    is_up: boolean;
    speed: number;
  }>;
}

export function useSystemInfo() {
  return useQuery<SystemInfo>({
    queryKey: ['systemInfo'],
    queryFn: async () => {
      const response = await api.get('/system/info');
      return response.data;
    },
    refetchInterval: 60000, // Aktualisiere alle 60 Sekunden
    staleTime: 30000, // Daten sind 30 Sekunden gültig
  });
}