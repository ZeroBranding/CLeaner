import React, { useState } from 'react'
import { useTheme } from '@/contexts/ThemeContext'
import {
  Cog6ToothIcon,
  SunIcon,
  MoonIcon,
  ComputerDesktopIcon,
  BellIcon,
  ShieldCheckIcon,
  ClockIcon,
  TrashIcon
} from '@heroicons/react/24/outline'

const Settings: React.FC = () => {
  const { theme, setTheme, isDark } = useTheme()
  const [settings, setSettings] = useState({
    autoCleanup: true,
    autoDriverCheck: false,
    notifications: true,
    startupWithSystem: true,
    backupBeforeCleanup: true,
    scanInterval: 'weekly',
    language: 'de',
    autoUpdate: true
  })

  const handleSettingChange = (key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }))
  }

  const scanIntervals = [
    { value: 'daily', label: 'Täglich' },
    { value: 'weekly', label: 'Wöchentlich' },
    { value: 'monthly', label: 'Monatlich' },
    { value: 'never', label: 'Nie' }
  ]

  const languages = [
    { value: 'de', label: 'Deutsch' },
    { value: 'en', label: 'English' },
    { value: 'fr', label: 'Français' },
    { value: 'es', label: 'Español' }
  ]
  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Einstellungen</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Passen Sie SystemCleaner Pro an Ihre Bedürfnisse an
        </p>
      </div>

      {/* Theme Settings */}
      <div className="card p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
          <Cog6ToothIcon className="w-5 h-5 mr-2" />
          Erscheinungsbild
        </h2>
        
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
              Theme
            </label>
            <div className="grid grid-cols-3 gap-3">
              <button
                onClick={() => setTheme('light')}
                className={`p-4 border rounded-lg flex flex-col items-center space-y-2 transition-colors ${
                  theme === 'light'
                    ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                    : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                }`}
              >
                <SunIcon className="w-6 h-6 text-yellow-500" />
                <span className="text-sm font-medium">Hell</span>
              </button>
              
              <button
                onClick={() => setTheme('dark')}
                className={`p-4 border rounded-lg flex flex-col items-center space-y-2 transition-colors ${
                  theme === 'dark'
                    ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                    : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                }`}
              >
                <MoonIcon className="w-6 h-6 text-blue-500" />
                <span className="text-sm font-medium">Dunkel</span>
              </button>
              
              <button
                onClick={() => setTheme('system')}
                className={`p-4 border rounded-lg flex flex-col items-center space-y-2 transition-colors ${
                  theme === 'system'
                    ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                    : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                }`}
              >
                <ComputerDesktopIcon className="w-6 h-6 text-gray-500" />
                <span className="text-sm font-medium">System</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Automation Settings */}
      <div className="card p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
          <ClockIcon className="w-5 h-5 mr-2" />
          Automatisierung
        </h2>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-medium text-gray-900 dark:text-white">Automatische Bereinigung</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Führt regelmäßige Systembereinigungen automatisch durch
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings.autoCleanup}
                onChange={(e) => handleSettingChange('autoCleanup', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary-600"></div>
            </label>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-medium text-gray-900 dark:text-white">Automatische Treiber-Prüfung</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Überprüft regelmäßig auf verfügbare Treiber-Updates
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings.autoDriverCheck}
                onChange={(e) => handleSettingChange('autoDriverCheck', e.target.checked)}
                className="sr-only peer"
                aria-label="Automatische Treiber-Prüfung aktivieren/deaktivieren"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary-600"></div>
            </label>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-medium text-gray-900 dark:text-white">Mit System starten</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                SystemCleaner Pro beim Systemstart automatisch öffnen
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings.startupWithSystem}
                onChange={(e) => handleSettingChange('startupWithSystem', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary-600"></div>
            </label>
          </div>

          <div>
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
              Scan-Intervall
            </label>
            <select
              value={settings.scanInterval}
              onChange={(e) => handleSettingChange('scanInterval', e.target.value)}
              className="input w-full md:w-64"
            >
              {scanIntervals.map(interval => (
                <option key={interval.value} value={interval.value}>
                  {interval.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Notification Settings */}
      <div className="card p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
          <BellIcon className="w-5 h-5 mr-2" />
          Benachrichtigungen
        </h2>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-medium text-gray-900 dark:text-white">Benachrichtigungen aktivieren</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Erhalten Sie Benachrichtigungen über System-Updates und Probleme
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings.notifications}
                onChange={(e) => handleSettingChange('notifications', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary-600"></div>
            </label>
          </div>
        </div>
      </div>

      {/* Security Settings */}
      <div className="card p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
          <ShieldCheckIcon className="w-5 h-5 mr-2" />
          Sicherheit
        </h2>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-medium text-gray-900 dark:text-white">Backup vor Bereinigung</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Erstellt automatisch ein Backup vor der Systembereinigung
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings.backupBeforeCleanup}
                onChange={(e) => handleSettingChange('backupBeforeCleanup', e.target.checked)}
                className="sr-only peer"
                aria-label="Backup vor Bereinigung aktivieren"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary-600"></div>
            </label>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-medium text-gray-900 dark:text-white">Automatische Updates</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                SystemCleaner Pro automatisch auf die neueste Version aktualisieren
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings.autoUpdate}
                onChange={(e) => handleSettingChange('autoUpdate', e.target.checked)}
                className="sr-only peer"
                aria-label="Automatische Updates aktivieren"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary-600"></div>
            </label>
          </div>
        </div>
      </div>

      {/* Language Settings */}
      <div className="card p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Sprache</h2>
        
        <div>
          <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
            Sprache auswählen
          </label>
          <select
            value={settings.language}
            onChange={(e) => handleSettingChange('language', e.target.value)}
            className="input w-full md:w-64"
            aria-label="Sprache auswählen"
          >
            {languages.map(lang => (
              <option key={lang.value} value={lang.value}>
                {lang.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Data Management */}
      <div className="card p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
          <TrashIcon className="w-5 h-5 mr-2" />
          Datenverwaltung
        </h2>
        
        <div className="space-y-4">
          <button className="btn-secondary">
            Cache-Daten löschen
          </button>
          <button className="btn-secondary">
            Einstellungen zurücksetzen
          </button>
          <button className="btn-secondary">
            Alle Daten exportieren
          </button>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex justify-end">
        <button className="btn-primary">
          Einstellungen speichern
        </button>
      </div>
    </div>
  )
}

export default Settings
