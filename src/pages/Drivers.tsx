import React, { useState } from 'react'
import { useSystem } from '@/contexts/SystemContext'
import {
  CpuChipIcon,
  ArrowDownTrayIcon,
  CheckIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  PlayIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline'

const Drivers: React.FC = () => {
  const { drivers, checkDrivers, isCheckingDrivers } = useSystem()
  const [selectedDrivers, setSelectedDrivers] = useState<string[]>([])

  const handleDriverSelect = (driverId: string) => {
    setSelectedDrivers(prev => 
      prev.includes(driverId) 
        ? prev.filter(id => id !== driverId)
        : [...prev, driverId]
    )
  }

  const handleSelectAll = () => {
    const outdatedDrivers = drivers.filter(d => d.status === 'outdated').map(d => d.name)
    setSelectedDrivers(outdatedDrivers)
  }

  const handleDeselectAll = () => {
    setSelectedDrivers([])
  }

  const handleUpdateSelected = () => {
    // Mock update functionality
    console.log('Updating drivers:', selectedDrivers)
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'up-to-date':
        return <CheckIcon className="w-4 h-4 text-green-500" />
      case 'outdated':
        return <ExclamationTriangleIcon className="w-4 h-4 text-yellow-500" />
      case 'missing':
        return <ExclamationTriangleIcon className="w-4 h-4 text-red-500" />
      default:
        return <ClockIcon className="w-4 h-4 text-gray-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'up-to-date':
        return 'status-success'
      case 'outdated':
        return 'status-warning'
      case 'missing':
        return 'status-danger'
      default:
        return 'status-info'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'up-to-date':
        return 'Aktuell'
      case 'outdated':
        return 'Veraltet'
      case 'missing':
        return 'Fehlt'
      default:
        return 'Unbekannt'
    }
  }

  const outdatedCount = drivers.filter(d => d.status === 'outdated').length
  const upToDateCount = drivers.filter(d => d.status === 'up-to-date').length

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Treiber-Management</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Überprüfen und aktualisieren Sie Ihre Systemtreiber für optimale Performance
          </p>
        </div>
        <button
          onClick={checkDrivers}
          disabled={isCheckingDrivers}
          className="btn-primary"
        >
          {isCheckingDrivers ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
              Prüfe Treiber...
            </>
          ) : (
            <>
              <ArrowPathIcon className="w-4 h-4 mr-2" />
              Treiber prüfen
            </>
          )}
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Gesamt Treiber</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{drivers.length}</p>
            </div>
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
              <CpuChipIcon className="w-6 h-6 text-white" />
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Aktuell</p>
              <p className="text-2xl font-bold text-green-600">{upToDateCount}</p>
            </div>
            <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-green-600 rounded-lg flex items-center justify-center">
              <CheckIcon className="w-6 h-6 text-white" />
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Veraltet</p>
              <p className="text-2xl font-bold text-yellow-600">{outdatedCount}</p>
            </div>
            <div className="w-12 h-12 bg-gradient-to-br from-yellow-500 to-yellow-600 rounded-lg flex items-center justify-center">
              <ExclamationTriangleIcon className="w-6 h-6 text-white" />
            </div>
          </div>
        </div>
      </div>

      {/* Drivers List */}
      <div className="card p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Treiber-Übersicht</h2>
          <div className="flex space-x-3">
            <button
              onClick={handleSelectAll}
              className="btn-secondary"
            >
              Alle veraltete auswählen
            </button>
            <button
              onClick={handleDeselectAll}
              className="btn-secondary"
            >
              Alle abwählen
            </button>
          </div>
        </div>

        <div className="space-y-4">
          {drivers.map((driver) => (
            <div
              key={driver.name}
              className={`p-4 border rounded-lg transition-colors ${
                selectedDrivers.includes(driver.name)
                  ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                  : 'border-gray-200 dark:border-gray-700'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <input
                    type="checkbox"
                    checked={selectedDrivers.includes(driver.name)}
                    onChange={() => handleDriverSelect(driver.name)}
                    disabled={driver.status === 'up-to-date'}
                    className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                  />
                  
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center">
                      <CpuChipIcon className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                    </div>
                    
                    <div>
                      <h3 className="font-medium text-gray-900 dark:text-white">{driver.name}</h3>
                      <div className="flex items-center space-x-4 mt-1">
                        <span className="text-sm text-gray-600 dark:text-gray-400">
                          Version: {driver.version}
                        </span>
                        <span className="text-sm text-gray-600 dark:text-gray-400">
                          Hersteller: {driver.manufacturer}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-4">
                  <div className={`${getStatusColor(driver.status)}`}>
                    {getStatusIcon(driver.status)}
                    <span>{getStatusText(driver.status)}</span>
                  </div>
                  
                  {driver.status === 'outdated' && driver.updateAvailable && (
                    <div className="text-right">
                      <p className="text-sm text-gray-600 dark:text-gray-400">Update verfügbar:</p>
                      <p className="text-sm font-medium text-primary-600">{driver.updateAvailable}</p>
                    </div>
                  )}
                  
                  {driver.status === 'outdated' && (
                    <button className="btn-primary">
                      <ArrowDownTrayIcon className="w-4 h-4 mr-2" />
                      Update
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {selectedDrivers.length > 0 && (
          <div className="mt-6 p-4 bg-primary-50 dark:bg-primary-900/20 border border-primary-200 dark:border-primary-800 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium text-primary-800 dark:text-primary-200">
                  {selectedDrivers.length} Treiber ausgewählt
                </h3>
                <p className="text-sm text-primary-600 dark:text-primary-400 mt-1">
                  Bereit für die Aktualisierung
                </p>
              </div>
              <button
                onClick={handleUpdateSelected}
                className="btn-primary"
              >
                <PlayIcon className="w-4 h-4 mr-2" />
                Ausgewählte aktualisieren
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Tips */}
      <div className="card p-6 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800">
        <h3 className="font-medium text-blue-800 dark:text-blue-200 mb-2">Tipps für Treiber-Updates</h3>
        <ul className="text-sm text-blue-700 dark:text-blue-300 space-y-1">
          <li>• Aktualisieren Sie Treiber regelmäßig für bessere Performance und Sicherheit</li>
          <li>• Erstellen Sie vor Updates ein System-Backup</li>
          <li>• Installieren Sie nur Treiber von vertrauenswürdigen Quellen</li>
          <li>• Starten Sie das System nach wichtigen Treiber-Updates neu</li>
        </ul>
      </div>
    </div>
  )
}

export default Drivers
