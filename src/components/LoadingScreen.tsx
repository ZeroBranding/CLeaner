import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

interface LoadingScreenProps {
  message?: string;
  progress?: number;
}

const LoadingScreen: React.FC<LoadingScreenProps> = ({ 
  message = 'System wird initialisiert...', 
  progress 
}) => {
  const [dots, setDots] = useState('');
  
  useEffect(() => {
    const interval = setInterval(() => {
      setDots(prev => prev.length >= 3 ? '' : prev + '.');
    }, 500);
    
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="fixed inset-0 bg-dark-bg-primary flex items-center justify-center z-50">
      <div className="text-center">
        {/* Logo Animation */}
        <motion.div 
          className="relative w-40 h-40 mx-auto mb-8"
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          {/* Outer Ring */}
          <motion.div 
            className="absolute inset-0 rounded-full border-4 border-primary-500/20"
            animate={{ rotate: 360 }}
            transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
          />
          
          {/* Middle Ring */}
          <motion.div 
            className="absolute inset-2 rounded-full border-4 border-primary-500/40 border-t-primary-500"
            animate={{ rotate: -360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          />
          
          {/* Inner Ring */}
          <motion.div 
            className="absolute inset-4 rounded-full border-4 border-secondary-500/40 border-b-secondary-500"
            animate={{ rotate: 360 }}
            transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
          />
          
          {/* Center Glow */}
          <motion.div 
            className="absolute inset-8 rounded-full bg-primary-500/20"
            animate={{ 
              scale: [1, 1.2, 1],
              opacity: [0.5, 0.8, 0.5]
            }}
            transition={{ duration: 2, repeat: Infinity }}
          />
          
          {/* Icon */}
          <div className="absolute inset-0 flex items-center justify-center">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.3, type: "spring", stiffness: 200 }}
              className="text-4xl font-bold text-primary-500"
            >
              GC
            </motion.div>
          </div>
        </motion.div>

        {/* Title */}
        <motion.h1 
          className="text-3xl font-bold text-white mb-2"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          GermanCodeZero Cleaner
        </motion.h1>

        {/* Message */}
        <motion.p 
          className="text-gray-400 mb-8"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
        >
          {message}{dots}
        </motion.p>

        {/* Progress Bar */}
        {progress !== undefined && (
          <motion.div 
            className="w-64 mx-auto"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.6 }}
          >
            <div className="bg-dark-bg-secondary rounded-full h-2 overflow-hidden">
              <motion.div 
                className="h-full bg-gradient-to-r from-primary-500 to-secondary-500"
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.3 }}
              />
            </div>
            <p className="text-xs text-gray-500 mt-2">{Math.round(progress)}%</p>
          </motion.div>
        )}

        {/* Loading Tips */}
        <motion.div
          className="mt-12 max-w-md mx-auto"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
        >
          <LoadingTip />
        </motion.div>
      </div>
    </div>
  );
};

// Loading Tips Component
const LoadingTip: React.FC = () => {
  const tips = [
    "Wussten Sie? Der Cleaner nutzt KI für intelligente Datei-Analyse.",
    "Tipp: Führen Sie regelmäßige Scans durch für optimale Performance.",
    "Mit Hardware-Beschleunigung werden Scans bis zu 3x schneller.",
    "Die 3D-Visualisierung zeigt Ihren Systemzustand in Echtzeit.",
    "Premium-Nutzer erhalten erweiterte Statistiken und Priority-Support."
  ];

  const [currentTip, setCurrentTip] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTip(prev => (prev + 1) % tips.length);
    }, 4000);
    
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="text-center">
      <p className="text-xs text-gray-500 mb-2">💡 Tipp</p>
      <motion.p 
        key={currentTip}
        className="text-sm text-gray-400"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        transition={{ duration: 0.5 }}
      >
        {tips[currentTip]}
      </motion.p>
    </div>
  );
};

export default LoadingScreen;