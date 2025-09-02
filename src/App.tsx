import React from 'react';
import './styles/globals.css';
import HologramScanner from '@components/3d/HologramScanner';
import { useHologramStore } from '@/store/hologramStore';

function App() {
  const triggerBurst = useHologramStore((s) => s.triggerBurst);
  return (
    <div className="relative w-screen h-screen overflow-hidden bg-black">
      <HologramScanner />
      <div className="absolute inset-x-0 top-0 z-10 p-4 text-center text-cyan-300/80 tracking-wider">
        3D Hologramm-Scanner Demo
      </div>
      <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-10 flex gap-3">
        <button
          onClick={() => triggerBurst(150)}
          className="px-4 py-2 rounded bg-cyan-500/20 border border-cyan-400/40 text-cyan-200 hover:bg-cyan-500/30 transition"
        >
          Datei-Burst (150)
        </button>
        <button
          onClick={() => triggerBurst(400)}
          className="px-4 py-2 rounded bg-cyan-500/20 border border-cyan-400/40 text-cyan-200 hover:bg-cyan-500/30 transition"
        >
          Großer Burst (400)
        </button>
      </div>
    </div>
  );
}

export default App;