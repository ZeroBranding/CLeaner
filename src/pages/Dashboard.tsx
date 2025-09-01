import React from 'react'
import { useSystem } from '@/contexts/SystemContext'
import {
  CpuChipIcon,
  TrashIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ArrowPathIcon,
  ChartBarIcon,
  ShieldCheckIcon,
  CogIcon
} from '@heroicons/react/24/outline'

const Dashboard: React.FC = () => {
  const {
    systemInfo,
    drivers,
    isAnalyzing,
    isCleaning,
    isCheckingDrivers,
    analyzeSystem,
    performCleanup,
    checkDrivers,
    error
  } = useSystem()

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const getSystemHealth = () => {
    if (!systemInfo) return { score: 0, status: 'unknown', color: 'text-gray-500' }
    
    const memoryUsage = ((systemInfo.totalMemory - systemInfo.freeMemory) / systemInfo.totalMemory) * 100
    const cpuUsage = systemInfo.cpuUsage
    const diskUsage = systemInfo.diskUsage
    
    const score = Math.max(0, 100 - (memoryUsage + cpuUsage + diskUsage) / 3)
    
    if (score >= 80) return { score, status: 'Excellent', color: 'text-green-500' }
    if (score >= 60) return { score, status: 'Good', color: 'text-yellow-500' }
    if (score >= 40) return { score, status: 'Fair', color: 'text-orange-500' }
    return { score, status: 'Poor', color: 'text-red-500' }
  }

  const systemHealth = getSystemHealth()
  const outdatedDrivers = drivers.filter(d => d.status === 'outdated').length

  const quickActions = [
    {
      name: 'System analysieren',
      description: 'Automatische Systemanalyse durchführen',
      icon: ChartBarIcon,
      action: analyzeSystem,
      loading: isAnalyzing,
      color: 'bg-blue-500 hover:bg-blue-600'
    },
    {
      name: 'Bereinigung starten',
      description: 'Cache und temporäre Dateien löschen',
      icon: TrashIcon,
      action: () => performCleanup({}),
      loading: isCleaning,
      color: 'bg-green-500 hover:bg-green-600'
    },
    {
      name: 'Treiber prüfen',
      description: 'Veraltete Treiber finden und aktualisieren',
      icon: CpuChipIcon,
      action: checkDrivers,
      loading: isCheckingDrivers,
      color: 'bg-purple-500 hover:bg-purple-600'
    }
  ]

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Willkommen bei SystemCleaner Pro - Ihr intelligenter System-Optimierer
          </p>
        </div>
        <button
          onClick={() => window.location.reload()}
          className="btn-secondary"
        >
          <ArrowPathIcon className="w-4 h-4 mr-2" />
          Aktualisieren
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <div className="flex items-center">
            <ExclamationTriangleIcon className="w-5 h-5 text-red-500 mr-2" />
            <span className="text-red-700 dark:text-red-300">{error}</span>
          </div>
        </div>
      )}

      {/* System Health Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">System Health</p>
              <p className={`text-2xl font-bold ${systemHealth.color}`}>
                {systemHealth.score.toFixed(0)}%
              </p>
              <p className={`text-sm ${systemHealth.color}`}>{systemHealth.status}</p>
            </div>
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
              <ShieldCheckIcon className="w-6 h-6 text-white" />
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">CPU Auslastung</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {systemInfo?.cpuUsage || 0}%
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400">Aktuell</p>
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
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {systemInfo ? formatBytes(systemInfo.totalMemory - systemInfo.freeMemory) : '0 GB'}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                von {systemInfo ? formatBytes(systemInfo.totalMemory) : '0 GB'}
              </p>
            </div>
            <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg flex items-center justify-center">
              <ChartBarIcon className="w-6 h-6 text-white" />
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Veraltete Treiber</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {outdatedDrivers}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400">Update verfügbar</p>
            </div>
            <div className="w-12 h-12 bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg flex items-center justify-center">
              <CogIcon className="w-6 h-6 text-white" />
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">Schnellaktionen</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {quickActions.map((action) => (
            <button
              key={action.name}
              onClick={action.action}
              disabled={action.loading}
              className={`${action.color} text-white rounded-lg p-4 text-left transition-colors disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium">{action.name}</h3>
                  <p className="text-sm opacity-90 mt-1">{action.description}</p>
                </div>
                {action.loading ? (
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                ) : (
                  <action.icon className="w-5 h-5" />
                )}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="card p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">Letzte Aktivitäten</h2>
        <div className="space-y-4">
          <div className="flex items-center space-x-3">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span className="text-sm text-gray-600 dark:text-gray-400">
              Systemanalyse abgeschlossen - 2 veraltete Treiber gefunden
            </span>
            <span className="text-xs text-gray-500">vor 5 Minuten</span>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
            <span className="text-sm text-gray-600 dark:text-gray-400">
              Cache-Bereinigung durchgeführt - 4.2 GB freigegeben
            </span>
            <span className="text-xs text-gray-500">vor 2 Stunden</span>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
            <span className="text-sm text-gray-600 dark:text-gray-400">
              NVIDIA Treiber erfolgreich aktualisiert
            </span>
            <span className="text-xs text-gray-500">vor 1 Tag</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
