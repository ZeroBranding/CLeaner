import { useSystem } from '@/contexts/SystemContext'
import {
  BellIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon
} from '@heroicons/react/24/outline'

const Header: React.FC = () => {
  const { systemInfo, isLoading } = useSystem()

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
    return `${hours}h ${minutes}m`
  }

  const getSystemStatus = () => {
    if (!systemInfo) return { status: 'unknown', icon: ClockIcon, color: 'text-gray-500' }
    
    const memoryUsage = ((systemInfo.totalMemory - systemInfo.freeMemory) / systemInfo.totalMemory) * 100
    const cpuUsage = systemInfo.cpuUsage
    const diskUsage = systemInfo.diskUsage

    if (memoryUsage > 90 || cpuUsage > 90 || diskUsage > 90) {
      return { status: 'critical', icon: ExclamationTriangleIcon, color: 'text-red-500' }
    } else if (memoryUsage > 70 || cpuUsage > 70 || diskUsage > 70) {
      return { status: 'warning', icon: ExclamationTriangleIcon, color: 'text-yellow-500' }
    } else {
      return { status: 'healthy', icon: CheckCircleIcon, color: 'text-green-500' }
    }
  }

  const systemStatus = getSystemStatus()
  return (
    <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* System Status */}
        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-2">
            <systemStatus.icon className={`w-5 h-5 ${systemStatus.color}`} />
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              System Status: {systemStatus.status}
            </span>
          </div>

          {systemInfo && (
            <>
              <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
                <span>RAM: {formatBytes(systemInfo.totalMemory - systemInfo.freeMemory)} / {formatBytes(systemInfo.totalMemory)}</span>
              </div>
              <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
                <span>CPU: {systemInfo.cpuUsage}%</span>
              </div>
              <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
                <span>Disk: {systemInfo.diskUsage}%</span>
              </div>
              <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
                <ClockIcon className="w-4 h-4" />
                <span>Uptime: {formatUptime(systemInfo.uptime)}</span>
              </div>
            </>
          )}
        </div>

        {/* Quick Actions */}
        <div className="flex items-center space-x-4">
          <button 
            className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
            aria-label="Notifications"
            type="button"
          >
            <BellIcon className="w-5 h-5" />
          </button>
          
          {isLoading && (
            <div className="flex items-center space-x-2 text-sm text-gray-500">
              <div className="w-4 h-4 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
              <span>Laden...</span>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}

export default Header
