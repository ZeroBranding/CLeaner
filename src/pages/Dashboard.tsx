import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { 
  HardDrive, 
  Cpu, 
  MemoryStick, 
  Zap, 
  AlertCircle,
  TrendingUp,
  Shield,
  Activity
} from 'lucide-react';

// Components
import StatCard from '@components/dashboard/StatCard';
import SystemChart from '@components/dashboard/SystemChart';
import QuickActions from '@components/dashboard/QuickActions';
import RecentScans from '@components/dashboard/RecentScans';
import SystemHealth from '@components/dashboard/SystemHealth';
import HologramScanner from '@components/3d/HologramScanner';

// Hooks & API
import { useSystemInfo } from '@hooks/useSystemInfo';
import { useSystemUsage } from '@hooks/useSystemUsage';
import { useScanHistory } from '@hooks/useScanHistory';

// Utils
import { formatBytes, formatPercentage } from '@utils/format';

const Dashboard: React.FC = () => {
  const { data: systemInfo, isLoading: infoLoading } = useSystemInfo();
  const { data: systemUsage } = useSystemUsage();
  const { data: scanHistory } = useScanHistory(7); // Letzte 7 Tage
  
  const [healthScore, setHealthScore] = useState(0);

  useEffect(() => {
    // Berechne Gesundheitsscore
    if (systemUsage) {
      const cpuScore = 100 - systemUsage.cpu.overall;
      const memoryScore = 100 - systemUsage.memory.percent;
      const diskScore = systemInfo?.disk.reduce((acc, d) => acc + (100 - d.percent), 0) / (systemInfo?.disk.length || 1);
      
      const totalScore = (cpuScore + memoryScore + diskScore) / 3;
      setHealthScore(Math.round(totalScore));
    }
  }, [systemUsage, systemInfo]);

  return (
    <div className="relative min-h-screen">
      {/* 3D Hologram Scanner */}
      <div className="absolute inset-0 z-0">
        <HologramScanner />
      </div>
      
      <div className="relative z-10 p-6">
        {/* Header */}
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold text-white mb-2">
            System Dashboard
          </h1>
          <p className="text-gray-400">
            Übersicht über Ihr System und letzte Aktivitäten
          </p>
        </motion.div>

        {/* Main Stats Grid */}
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
        >
          <StatCard
            title="System-Gesundheit"
            value={`${healthScore}%`}
            icon={<Shield className="w-6 h-6" />}
            trend={healthScore > 70 ? 'up' : 'down'}
            color={healthScore > 70 ? 'green' : healthScore > 40 ? 'yellow' : 'red'}
            description="Gesamtbewertung"
          />
          
          <StatCard
            title="CPU-Auslastung"
            value={formatPercentage(systemUsage?.cpu.overall || 0)}
            icon={<Cpu className="w-6 h-6" />}
            sparklineData={systemUsage?.cpu.history || []}
            color="blue"
            description={`${systemInfo?.cpu.cores || 0} Kerne`}
          />
          
          <StatCard
            title="Arbeitsspeicher"
            value={formatPercentage(systemUsage?.memory.percent || 0)}
            icon={<MemoryStick className="w-6 h-6" />}
            sparklineData={systemUsage?.memory.history || []}
            color="purple"
            description={formatBytes(systemInfo?.memory.total || 0)}
          />
          
          <StatCard
            title="Speicherplatz"
            value={formatBytes(systemInfo?.disk[0]?.free || 0)}
            icon={<HardDrive className="w-6 h-6" />}
            color="cyan"
            description="Verfügbar"
            subValue={`${systemInfo?.disk[0]?.percent || 0}% belegt`}
          />
        </motion.div>

        {/* Charts and Activity Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* System Performance Chart */}
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="lg:col-span-2"
          >
            <SystemChart 
              cpuData={systemUsage?.cpu.history || []}
              memoryData={systemUsage?.memory.history || []}
              diskData={systemUsage?.disk.history || []}
            />
          </motion.div>

          {/* System Health */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
          >
            <SystemHealth 
              score={healthScore}
              components={{
                cpu: systemUsage?.cpu.overall || 0,
                memory: systemUsage?.memory.percent || 0,
                disk: systemInfo?.disk[0]?.percent || 0,
                temperature: systemUsage?.gpu?.temperature || 0
              }}
            />
          </motion.div>
        </div>

        {/* Quick Actions and Recent Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Quick Actions */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <QuickActions />
          </motion.div>

          {/* Recent Scans */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <RecentScans scans={scanHistory || []} />
          </motion.div>
        </div>

        {/* Alerts */}
        {systemUsage?.cpu.overall > 80 && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="fixed bottom-6 right-6 bg-red-500/20 backdrop-blur-md border border-red-500/50 rounded-lg p-4 max-w-sm"
          >
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-400 mt-0.5" />
              <div>
                <h4 className="text-white font-semibold mb-1">Hohe CPU-Auslastung</h4>
                <p className="text-gray-300 text-sm">
                  Die CPU-Auslastung liegt bei {Math.round(systemUsage.cpu.overall)}%. 
                  Ein System-Scan wird empfohlen.
                </p>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;