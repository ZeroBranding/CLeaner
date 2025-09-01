import React from 'react'
import { NavLink } from 'react-router-dom'
import { useTheme } from '@/contexts/ThemeContext'
import {
  HomeIcon,
  ChatBubbleLeftRightIcon,
  TrashIcon,
  CpuChipIcon,
  Cog6ToothIcon,
  InformationCircleIcon,
  SunIcon,
  MoonIcon,
  ComputerDesktopIcon
} from '@heroicons/react/24/outline'

const Sidebar: React.FC = () => {
  const { theme, setTheme, isDark } = useTheme()

  const navigation = [
    { name: 'Dashboard', href: '/', icon: HomeIcon },
    { name: 'KI-Chat', href: '/chat', icon: ChatBubbleLeftRightIcon },
    { name: 'Bereinigung', href: '/cleanup', icon: TrashIcon },
    { name: 'Treiber', href: '/drivers', icon: CpuChipIcon },
    { name: 'System Info', href: '/system', icon: InformationCircleIcon },
    { name: 'Einstellungen', href: '/settings', icon: Cog6ToothIcon },
  ]

  const toggleTheme = () => {
    setTheme(isDark ? 'light' : 'dark')
  }

  return (
    <div className="flex flex-col w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700">
      {/* Logo */}
      <div className="flex items-center justify-center h-16 px-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg flex items-center justify-center">
            <ComputerDesktopIcon className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-gray-900 dark:text-white">SystemCleaner</h1>
            <p className="text-xs text-gray-500 dark:text-gray-400">Pro</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-2">
        {navigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            className={({ isActive }) =>
              `sidebar-item ${isActive ? 'active' : ''}`
            }
          >
            <item.icon className="w-5 h-5" />
            <span>{item.name}</span>
          </NavLink>
        ))}
      </nav>

      {/* Theme Toggle */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        <button
          onClick={toggleTheme}
          className="flex items-center justify-center w-full px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
        >
          {isDark ? (
            <>
              <SunIcon className="w-5 h-5 mr-2" />
              <span>Light Mode</span>
            </>
          ) : (
            <>
              <MoonIcon className="w-5 h-5 mr-2" />
              <span>Dark Mode</span>
            </>
          )}
        </button>
      </div>
    </div>
  )
}

export default Sidebar
