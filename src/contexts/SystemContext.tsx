import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'

interface SystemInfo {
  os: string
  version: string
  arch: string
  platform: string
  hostname: string
  uptime: number
  totalMemory: number
  freeMemory: number
  cpuUsage: number
  diskUsage: number
}

interface CleanupResult {
  type: string
  cleaned: number
  freed: number
  errors: string[]
}

interface DriverInfo {
  name: string
  version: string
  manufacturer: string
  status: 'up-to-date' | 'outdated' | 'missing'
  updateAvailable?: string
}

interface SystemContextType {
  systemInfo: SystemInfo | null
  isLoading: boolean
  error: string | null
  cleanupResults: CleanupResult[]
  drivers: DriverInfo[]
  isAnalyzing: boolean
  isCleaning: boolean
  isCheckingDrivers: boolean
  analyzeSystem: () => Promise<void>
  performCleanup: (options: any) => Promise<void>
  checkDrivers: () => Promise<void>
  refreshSystemInfo: () => Promise<void>
}

const SystemContext = createContext<SystemContextType | undefined>(undefined)

export const useSystem = () => {
  const context = useContext(SystemContext)
  if (context === undefined) {
    throw new Error('useSystem must be used within a SystemProvider')
  }
  return context
}

interface SystemProviderProps {
  children: React.ReactNode
}

export const SystemProvider: React.FC<SystemProviderProps> = ({ children }) => {
  const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [cleanupResults, setCleanupResults] = useState<CleanupResult[]>([])
  const [drivers, setDrivers] = useState<DriverInfo[]>([])
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [isCleaning, setIsCleaning] = useState(false)
  const [isCheckingDrivers, setIsCheckingDrivers] = useState(false)

  const refreshSystemInfo = useCallback(async () => {
    try {
      setIsLoading(true)
      setError(null)
      
      // Mock system info for now - will be replaced with actual API calls
      const mockSystemInfo: SystemInfo = {
        os: 'Linux',
        version: '6.12.8+',
        arch: 'x64',
        platform: 'linux',
        hostname: 'systemcleaner-pro',
        uptime: Date.now(),
        totalMemory: 16 * 1024 * 1024 * 1024, // 16GB
        freeMemory: 8 * 1024 * 1024 * 1024, // 8GB
        cpuUsage: 45,
        diskUsage: 75
      }
      
      setSystemInfo(mockSystemInfo)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred')
    } finally {
      setIsLoading(false)
    }
  }, [])

  const analyzeSystem = useCallback(async () => {
    try {
      setIsAnalyzing(true)
      setError(null)
      
      // Mock analysis - will be replaced with actual API calls
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // Simulate finding issues
      const mockDrivers: DriverInfo[] = [
        {
          name: 'NVIDIA Graphics Driver',
          version: '535.98',
          manufacturer: 'NVIDIA',
          status: 'outdated',
          updateAvailable: '545.84'
        },
        {
          name: 'Intel Network Adapter',
          version: '22.0.0',
          manufacturer: 'Intel',
          status: 'up-to-date'
        }
      ]
      
      setDrivers(mockDrivers)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed')
    } finally {
      setIsAnalyzing(false)
    }
  }, [])

  const performCleanup = useCallback(async (options: any) => {
    try {
      setIsCleaning(true)
      setError(null)
      
      // Mock cleanup - will be replaced with actual API calls
      await new Promise(resolve => setTimeout(resolve, 3000))
      
      const mockResults: CleanupResult[] = [
        {
          type: 'GPU Cache',
          cleaned: 15,
          freed: 2.5 * 1024 * 1024 * 1024, // 2.5GB
          errors: []
        },
        {
          type: 'System Cache',
          cleaned: 8,
          freed: 1.2 * 1024 * 1024 * 1024, // 1.2GB
          errors: []
        },
        {
          type: 'Browser Cache',
          cleaned: 3,
          freed: 500 * 1024 * 1024, // 500MB
          errors: []
        }
      ]
      
      setCleanupResults(mockResults)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Cleanup failed')
    } finally {
      setIsCleaning(false)
    }
  }, [])

  const checkDrivers = useCallback(async () => {
    try {
      setIsCheckingDrivers(true)
      setError(null)
      
      // Mock driver check - will be replaced with actual API calls
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      const mockDrivers: DriverInfo[] = [
        {
          name: 'NVIDIA Graphics Driver',
          version: '535.98',
          manufacturer: 'NVIDIA',
          status: 'outdated',
          updateAvailable: '545.84'
        },
        {
          name: 'Intel Network Adapter',
          version: '22.0.0',
          manufacturer: 'Intel',
          status: 'up-to-date'
        },
        {
          name: 'Realtek Audio Driver',
          version: '6.0.9421.1',
          manufacturer: 'Realtek',
          status: 'up-to-date'
        }
      ]
      
      setDrivers(mockDrivers)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Driver check failed')
    } finally {
      setIsCheckingDrivers(false)
    }
  }, [])

  useEffect(() => {
    refreshSystemInfo()
  }, [refreshSystemInfo])

  const value: SystemContextType = {
    systemInfo,
    isLoading,
    error,
    cleanupResults,
    drivers,
    isAnalyzing,
    isCleaning,
    isCheckingDrivers,
    analyzeSystem,
    performCleanup,
    checkDrivers,
    refreshSystemInfo
  }

  return (
    <SystemContext.Provider value={value}>
      {children}
    </SystemContext.Provider>
  )
}
