import React from 'react'
import { useSystem } from '@/contexts/SystemContext'
import {
  ComputerDesktopIcon,
  CpuChipIcon,
  HardDriveIcon,
  GlobeAltIcon,
  ClockIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline'

const SystemInfo: React.FC = () => {
  const { systemInfo } = useSystem()

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatUptime = (uptime: number): string => {
    const hours = Math.floor(uptime / (1000 * 60 * 60))
    const minutes = Math.floor((uptime % (1000 * 60 * 60)) / (1000 * 60))
    const seconds = Math.floor((uptime % (1000 * 60)) / 1000)
    return `${hours}h ${minutes}m ${seconds}s`
  }

  const mockSystemDetails = {
    cpu: {
      model: 'Intel Core i7-12700K',
      cores: 12,
      threads: 20,
      frequency: '3.6 GHz',
      maxFrequency: '5.0 GHz',
      architecture: 'x64',
      cache: '25 MB'
    },
    memory: {
      total: 16 * 1024 * 1024 * 1024, // 16GB
      used: 8 * 1024 * 1024 * 1024, // 8GB
      available: 8 * 1024 * 1024 * 1024, // 8GB
      slots: 4,
      type: 'DDR4',
      frequency: '3200 MHz'
    },
    storage: [
      {
        name: 'Samsung 970 EVO Plus',
        size: 1000 * 1024 * 1024 * 1024, // 1TB
        used: 750 * 1024 * 1024 * 1024, // 750GB
        type: 'NVMe SSD',
        health: 'Excellent'
      },
      {
        name: 'Seagate Barracuda',
        size: 2000 * 1024 * 1024 * 1024, // 2TB
        used: 1200 * 1024 * 1024 * 1024, // 1.2TB
        type: 'HDD',
        health: 'Good'
      }
    ],
    network: {
      interfaces: [
        {
          name: 'Ethernet',
          type: 'Gigabit',
          status: 'Connected',
          speed: '1 Gbps',
          ip: '192.168.1.100'
        },
        {
          name: 'Wi-Fi',
          type: '802.11ax',
          status: 'Connected',
          speed: '867 Mbps',
          ip: '192.168.1.101'
        }
      ]
    },
    graphics: [
      {
        name: 'NVIDIA GeForce RTX 3080',
        memory: 10 * 1024 * 1024 * 1024, // 10GB
        driver: '545.84',
        status: 'Active'
      }
    ]
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">System Information</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Detaillierte Informationen über Ihr System und Hardware
        </p>
      </div>

      {/* System Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Betriebssystem</p>
              <p className="text-lg font-semibold text-gray-900 dark:text-white">
                {systemInfo?.os || 'Linux'} {systemInfo?.version || '6.12.8+'}
              </p>
              <p className="text-sm text-gray-500">{systemInfo?.arch || 'x64'}</p>
            </div>
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
              <ComputerDesktopIcon className="w-6 h-6 text-white" />
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">CPU Auslastung</p>
              <p className="text-lg font-semibold text-gray-900 dark:text-white">
                {systemInfo?.cpuUsage || 0}%
              </p>
              <p className="text-sm text-gray-500">Aktuell</p>
            </div>
            <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-green-600 rounded-lg flex items-center justify-center">
              <CpuChipIcon className="w-6 h-6 text-white" />
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">RAM Verwendung</p>
              <p className="text-lg font-semibold text-gray-900 dark:text-white">
                {systemInfo ? formatBytes(systemInfo.totalMemory - systemInfo.freeMemory) : '0 GB'}
              </p>
              <p className="text-sm text-gray-500">
                von {systemInfo ? formatBytes(systemInfo.totalMemory) : '0 GB'}
              </p>
            </div>
            <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg flex items-center justify-center">
              <HardDriveIcon className="w-6 h-6 text-white" />
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Uptime</p>
              <p className="text-lg font-semibold text-gray-900 dark:text-white">
                {systemInfo ? formatUptime(systemInfo.uptime) : '0h 0m 0s'}
              </p>
              <p className="text-sm text-gray-500">System läuft</p>
            </div>
            <div className="w-12 h-12 bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg flex items-center justify-center">
              <ClockIcon className="w-6 h-6 text-white" />
            </div>
          </div>
        </div>
      </div>

      {/* Detailed Information */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* CPU Information */}
        <div className="card p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <CpuChipIcon className="w-5 h-5 mr-2" />
            Prozessor
          </h2>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Modell:</span>
              <span className="font-medium">{mockSystemDetails.cpu.model}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Kerne/Threads:</span>
              <span className="font-medium">{mockSystemDetails.cpu.cores} / {mockSystemDetails.cpu.threads}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Basis-Frequenz:</span>
              <span className="font-medium">{mockSystemDetails.cpu.frequency}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Max-Frequenz:</span>
              <span className="font-medium">{mockSystemDetails.cpu.maxFrequency}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Architektur:</span>
              <span className="font-medium">{mockSystemDetails.cpu.architecture}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Cache:</span>
              <span className="font-medium">{mockSystemDetails.cpu.cache}</span>
            </div>
          </div>
        </div>

        {/* Memory Information */}
        <div className="card p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <HardDriveIcon className="w-5 h-5 mr-2" />
            Arbeitsspeicher
          </h2>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Gesamt:</span>
              <span className="font-medium">{formatBytes(mockSystemDetails.memory.total)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Verwendet:</span>
              <span className="font-medium">{formatBytes(mockSystemDetails.memory.used)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Verfügbar:</span>
              <span className="font-medium">{formatBytes(mockSystemDetails.memory.available)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Slots:</span>
              <span className="font-medium">{mockSystemDetails.memory.slots}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Typ:</span>
              <span className="font-medium">{mockSystemDetails.memory.type}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Frequenz:</span>
              <span className="font-medium">{mockSystemDetails.memory.frequency}</span>
            </div>
          </div>
        </div>

        {/* Storage Information */}
        <div className="card p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <HardDriveIcon className="w-5 h-5 mr-2" />
            Speicher
          </h2>
          <div className="space-y-4">
            {mockSystemDetails.storage.map((drive, index) => (
              <div key={index} className="border-b border-gray-200 dark:border-gray-700 pb-3 last:border-b-0">
                <div className="flex justify-between items-start mb-2">
                  <span className="font-medium text-gray-900 dark:text-white">{drive.name}</span>
                  <span className="text-sm text-gray-500">{drive.type}</span>
                </div>
                <div className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">Größe:</span>
                    <span>{formatBytes(drive.size)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">Verwendet:</span>
                    <span>{formatBytes(drive.used)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">Gesundheit:</span>
                    <span className={`font-medium ${
                      drive.health === 'Excellent' ? 'text-green-600' : 'text-yellow-600'
                    }`}>{drive.health}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Network Information */}
        <div className="card p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <GlobeAltIcon className="w-5 h-5 mr-2" />
            Netzwerk
          </h2>
          <div className="space-y-4">
            {mockSystemDetails.network.interfaces.map((interface_, index) => (
              <div key={index} className="border-b border-gray-200 dark:border-gray-700 pb-3 last:border-b-0">
                <div className="flex justify-between items-start mb-2">
                  <span className="font-medium text-gray-900 dark:text-white">{interface_.name}</span>
                  <span className={`text-sm px-2 py-1 rounded-full ${
                    interface_.status === 'Connected' 
                      ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
                      : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
                  }`}>
                    {interface_.status}
                  </span>
                </div>
                <div className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">Typ:</span>
                    <span>{interface_.type}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">Geschwindigkeit:</span>
                    <span>{interface_.speed}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">IP-Adresse:</span>
                    <span className="font-mono">{interface_.ip}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Graphics Information */}
      <div className="card p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
          <ComputerDesktopIcon className="w-5 h-5 mr-2" />
          Grafikkarten
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {mockSystemDetails.graphics.map((gpu, index) => (
            <div key={index} className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
              <div className="flex justify-between items-start mb-2">
                <span className="font-medium text-gray-900 dark:text-white">{gpu.name}</span>
                <span className={`text-sm px-2 py-1 rounded-full ${
                  gpu.status === 'Active' 
                    ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
                    : 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300'
                }`}>
                  {gpu.status}
                </span>
              </div>
              <div className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Speicher:</span>
                  <span>{formatBytes(gpu.memory)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Treiber:</span>
                  <span>{gpu.driver}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default SystemInfo
