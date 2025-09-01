import React from 'react';
import './styles/globals.css';
import HologramScanner from '@components/3d/HologramScanner';

function App() {
  return (
    <div className="relative w-screen h-screen overflow-hidden bg-black">
      <HologramScanner />
      <div className="absolute inset-x-0 top-0 z-10 p-4 text-center text-cyan-300/80 tracking-wider">
        3D Hologramm-Scanner Demo
      </div>
    </div>
  );
}

export default App;