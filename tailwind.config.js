/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#e6f9ff',
          100: '#b3edff',
          200: '#80e2ff',
          300: '#4dd6ff',
          400: '#1acaff',
          500: '#00d4ff', // Main cyan
          600: '#00a3cc',
          700: '#007399',
          800: '#004266',
          900: '#001133',
        },
        secondary: {
          50: '#f3e5ff',
          100: '#dbb8ff',
          200: '#c48aff',
          300: '#ac5dff',
          400: '#952fff',
          500: '#a855f7', // Purple
          600: '#7e02ff',
          700: '#5e00cc',
          800: '#3f0099',
          900: '#1f0066',
        },
        accent: {
          green: '#10b981',
          red: '#ef4444',
          yellow: '#f59e0b',
          blue: '#3b82f6',
        },
        dark: {
          bg: {
            primary: '#0a0a0a',
            secondary: '#1a1a1a',
            tertiary: '#2a2a2a',
            quaternary: '#3a3a3a',
          },
          text: {
            primary: '#ffffff',
            secondary: '#a1a1aa',
            tertiary: '#71717a',
          }
        }
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 3s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite',
        'scan': 'scan 2s linear infinite',
        'rotate-slow': 'rotate 10s linear infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        glow: {
          '0%, 100%': { 
            boxShadow: '0 0 20px rgba(0, 212, 255, 0.5)',
            borderColor: 'rgba(0, 212, 255, 0.5)',
          },
          '50%': { 
            boxShadow: '0 0 30px rgba(0, 212, 255, 0.8)',
            borderColor: 'rgba(0, 212, 255, 0.8)',
          },
        },
        scan: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100%)' },
        },
        rotate: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      backdropBlur: {
        xs: '2px',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'hologram': 'linear-gradient(45deg, transparent 30%, rgba(0, 212, 255, 0.1) 50%, transparent 70%)',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    // Custom plugin für Glassmorphism
    function({ addUtilities }) {
      addUtilities({
        '.glass': {
          background: 'rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
        },
        '.glass-dark': {
          background: 'rgba(0, 0, 0, 0.5)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
        },
        '.neon-glow': {
          textShadow: '0 0 10px currentColor, 0 0 20px currentColor',
        },
        '.hologram-effect': {
          background: 'linear-gradient(45deg, transparent 30%, rgba(0, 212, 255, 0.1) 50%, transparent 70%)',
          backgroundSize: '200% 200%',
          animation: 'hologram 2s linear infinite',
        },
      })
    },
  ],
}