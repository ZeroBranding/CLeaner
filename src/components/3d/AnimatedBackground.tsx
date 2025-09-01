import React, { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import HologramScanner from './HologramScanner';
import ParticleField from './ParticleField';

const AnimatedBackground: React.FC = () => {
  return (
    <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }}>
      <Canvas
        gl={{ antialias: true, alpha: true, powerPreference: 'high-performance' }}
        camera={{ fov: 45, near: 0.1, far: 200, position: [0, 1.6, 6] }}
      >
        <color attach="background" args={[0, 0, 0]} />
        <ambientLight intensity={0.2} />
        <directionalLight position={[5, 10, 5]} intensity={0.6} />

        <Suspense fallback={null}>
          <group position={[0, 0, 0]}> 
            <ParticleField count={3000} area={[12, 6, 12]} />
            <HologramScanner radius={1.4} height={2.2} position={[0, 1.1, 0]} />
          </group>
        </Suspense>

        {/* Controls sind deaktiviert, da die Szene als Hintergrund dient */}
        <OrbitControls enabled={false} />
      </Canvas>
    </div>
  );
};

export default AnimatedBackground;



