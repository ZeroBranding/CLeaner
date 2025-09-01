import React, { useState } from 'react'
import { useSystem } from '@/contexts/SystemContext'
import {
  TrashIcon,
  PlayIcon,
  CheckIcon,
  ExclamationTriangleIcon,
  ComputerDesktopIcon,
  CpuChipIcon,
  HardDriveIcon,
  GlobeAltIcon
} from '@heroicons/react/24/outline'

interface CleanupOption {
  id: string
  name: string
  description: string
  icon: React.ComponentType<any>
  category: string
  estimatedSize: string
  selected: boolean
}

const Cleanup: React.FC = () => {
  const { performCleanup, isCleaning, cleanupResults } = useSystem()
  const [selectedOptions, setSelectedOptions] = useState<string[]>([])
  const [showResults, setShowResults] = useState(false)

  const cleanupOptions: CleanupOption[] = [
    {
      id: 'gpu-cache',
      name: 'GPU Cache',
      description: 'NVIDIA, AMD und Intel Grafiktreiber Cache',
      icon: CpuChipIcon,
      category: 'Hardware',
      estimatedSize: '2.5 GB',
      selected: false
    },
    {
      id: 'cpu-cache',
      name: 'CPU Cache',
      description: 'Prozessor-spezifische Cache-Dateien',
      icon: ComputerDesktopIcon,
      category: 'Hardware',
      estimatedSize: '1.2 GB',
      selected: false
    },
    {
      id: 'ssd-cache',
      name: 'SSD/HDD Cache',
      description: 'Festplatten-Cache und temporäre Dateien',
      icon: HardDriveIcon,
      category: 'Storage',
      estimatedSize: '3.8 GB',
      selected: false
    },
    {
      id: 'browser-cache',
      name: 'Browser Cache',
      description: 'Chrome, Firefox, Safari, Edge Cache',
      icon: GlobeAltIcon,
      category: 'Applications',
      estimatedSize: '1.5 GB',
      selected: false
    },
    {
      id: 'system-cache',
      name: 'System Cache',
      description: 'Betriebssystem-Cache und Logs',
      icon: ComputerDesktopIcon,
      category: 'System',
      estimatedSize: '2.1 GB',
      selected: false
    },
    {
      id: 'temp-files',
      name: 'Temporäre Dateien',
      description: 'Temporäre Dateien und Downloads',
      icon: TrashIcon,
      category: 'System',
      estimatedSize: '4.2 GB',
      selected: false
    }
  ]

  const handleOptionToggle = (optionId: string) => {
    setSelectedOptions(prev => 
      prev.includes(optionId) 
        ? prev.filter(id => id !== optionId)
        : [...prev, optionId]
    )
  }

  const handleSelectAll = () => {
    setSelectedOptions(cleanupOptions.map(option => option.id))
  }

  const handleDeselectAll = () => {
    setSelectedOptions([])
  }

  const handleStartCleanup = async () => {
    if (selectedOptions.length === 0) return
    
    setShowResults(false)
    await performCleanup({ options: selectedOptions })
    setShowResults(true)
  }

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const totalEstimatedSize = cleanupOptions
    .filter(option => selectedOptions.includes(option.id))
    .reduce((total, option) => {
      const size = parseFloat(option.estimatedSize.split(' ')[0])
      const unit = option.estimatedSize.split(' ')[1]
      const multiplier = unit === 'GB' ? 1024 * 1024 * 1024 : unit === 'MB' ? 1024 * 1024 : 1024
      return total + (size * multiplier)
    }, 0)

  const categories = [...new Set(cleanupOptions.map(option => option.category))]

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">System Bereinigung</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Wählen Sie die zu bereinigenden Cache-Typen und starten Sie die Optimierung
        </p>
      </div>

      {/* Summary Card */}
      <div className="card p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Bereinigungsübersicht</h2>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              {selectedOptions.length} von {cleanupOptions.length} Optionen ausgewählt
            </p>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold text-primary-600">
              {formatBytes(totalEstimatedSize)}
            </p>
            <p className="text-sm text-gray-500">Geschätzter Speicherplatz</p>
          </div>
        </div>
      </div>

      {/* Cleanup Options */}
      <div className="space-y-6">
        {categories.map(category => (
          <div key={category} className="card p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">{category}</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {cleanupOptions
                .filter(option => option.category === category)
                .map(option => (
                  <div
                    key={option.id}
                    className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                      selectedOptions.includes(option.id)
                        ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                        : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                    }`}
                    onClick={() => handleOptionToggle(option.id)}
                  >
                    <div className="flex items-start space-x-3">
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                        selectedOptions.includes(option.id)
                          ? 'bg-primary-100 dark:bg-primary-900'
                          : 'bg-gray-100 dark:bg-gray-700'
                      }`}>
                        <option.icon className={`w-5 h-5 ${
                          selectedOptions.includes(option.id)
                            ? 'text-primary-600 dark:text-primary-400'
                            : 'text-gray-600 dark:text-gray-400'
                        }`} />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <h4 className="font-medium text-gray-900 dark:text-white">{option.name}</h4>
                          <div className="flex items-center space-x-2">
                            <span className="text-sm text-gray-500">{option.estimatedSize}</span>
                            {selectedOptions.includes(option.id) && (
                              <CheckIcon className="w-4 h-4 text-primary-600" />
                            )}
                          </div>
                        </div>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                          {option.description}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        ))}
      </div>

      {/* Action Buttons */}
      <div className="flex items-center justify-between">
        <div className="flex space-x-3">
          <button
            onClick={handleSelectAll}
            className="btn-secondary"
          >
            Alle auswählen
          </button>
          <button
            onClick={handleDeselectAll}
            className="btn-secondary"
          >
            Alle abwählen
          </button>
        </div>
        
        <button
          onClick={handleStartCleanup}
          disabled={selectedOptions.length === 0 || isCleaning}
          className="btn-primary"
        >
          {isCleaning ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
              Bereinigung läuft...
            </>
          ) : (
            <>
              <PlayIcon className="w-4 h-4 mr-2" />
              Bereinigung starten
            </>
          )}
        </button>
      </div>

      {/* Results */}
      {showResults && cleanupResults.length > 0 && (
        <div className="card p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Bereinigungsergebnisse</h2>
          <div className="space-y-4">
            {cleanupResults.map((result, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className="flex items-center space-x-3">
                  <CheckIcon className="w-5 h-5 text-green-500" />
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white">{result.type}</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {result.cleaned} Dateien bereinigt
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-medium text-green-600 dark:text-green-400">
                    {formatBytes(result.freed)}
                  </p>
                  <p className="text-sm text-gray-500">freigegeben</p>
                </div>
              </div>
            ))}
          </div>
          
          <div className="mt-6 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
            <div className="flex items-center">
              <CheckIcon className="w-5 h-5 text-green-500 mr-2" />
              <span className="text-green-700 dark:text-green-300 font-medium">
                Bereinigung erfolgreich abgeschlossen! 
                {formatBytes(cleanupResults.reduce((total, result) => total + result.freed, 0))} Speicherplatz freigegeben.
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Safety Notice */}
      <div className="card p-6 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800">
        <div className="flex items-start space-x-3">
          <ExclamationTriangleIcon className="w-5 h-5 text-yellow-500 mt-0.5" />
          <div>
            <h3 className="font-medium text-yellow-800 dark:text-yellow-200">Sicherheitshinweis</h3>
            <p className="text-sm text-yellow-700 dark:text-yellow-300 mt-1">
              Die Bereinigung entfernt nur temporäre Dateien und Cache-Daten. Ihre persönlichen Dateien und Programme bleiben unberührt. 
              Es wird empfohlen, vor der Bereinigung wichtige Daten zu sichern.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Cleanup
