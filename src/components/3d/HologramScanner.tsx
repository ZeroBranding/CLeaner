import React, { useMemo, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { AdaptiveDpr, OrbitControls } from '@react-three/drei';
import { EffectComposer, Bloom } from '@react-three/postprocessing';
import { useHologramStore } from '@/store/hologramStore';

type HologramScannerProps = {
  className?: string;
  style?: React.CSSProperties;
  /** Optional: Anzahl Partikel (Performance-Tuning). */
  particleCount?: number;
};

function HologramMaterial() {
  const materialRef = useRef<THREE.ShaderMaterial>(null);

  const uniforms = useMemo(
    () => ({
      u_time: { value: 0 },
      u_color: { value: new THREE.Color('#00E5FF') },
      u_glow: { value: 1.4 },
      u_scanSpeed: { value: 0.6 },
    }),
    []
  );

  useFrame((state) => {
    if (materialRef.current) {
      materialRef.current.uniforms.u_time.value = state.clock.getElapsedTime();
    }
  });

  const vertexShader = /* glsl */ `
    varying vec3 vNormal;
    varying vec3 vWorldPosition;
    void main() {
      vNormal = normalize(normalMatrix * normal);
      vec4 worldPosition = modelMatrix * vec4(position, 1.0);
      vWorldPosition = worldPosition.xyz;
      gl_Position = projectionMatrix * viewMatrix * worldPosition;
    }
  `;

  const fragmentShader = /* glsl */ `
    uniform float u_time;
    uniform vec3 u_color;
    uniform float u_glow;
    uniform float u_scanSpeed;
    varying vec3 vNormal;
    varying vec3 vWorldPosition;

    float fresnel(vec3 normal, vec3 viewDir) {
      return pow(1.0 - max(dot(normal, viewDir), 0.0), 2.0);
    }

    float scanLines(vec3 pos) {
      float lineFreq = 25.0; // Dichte der Linien
      float t = pos.y * lineFreq + u_time * u_scanSpeed * 20.0;
      float band = smoothstep(0.48, 0.52, fract(t));
      return band * 0.85;
    }

    void main() {
      vec3 viewDir = normalize(cameraPosition - vWorldPosition);
      float f = fresnel(normalize(vNormal), viewDir);
      float lines = scanLines(vWorldPosition);
      vec3 col = u_color * (f * u_glow + lines);
      gl_FragColor = vec4(col, clamp(f * 1.2 + lines, 0.15, 1.0));
    }
  `;

  return (
    <shaderMaterial
      ref={materialRef}
      uniforms={uniforms}
      vertexShader={vertexShader}
      fragmentShader={fragmentShader}
      transparent
      depthWrite={false}
      blending={THREE.AdditiveBlending}
    />
  );
}

function ScanPlane() {
  const meshRef = useRef<THREE.Mesh>(null);
  useFrame((state) => {
    const t = state.clock.getElapsedTime();
    const y = ((Math.sin(t * 0.8) + 1) * 0.5) * 2.2 - 1.1; // -1.1..+1.1
    if (meshRef.current) {
      meshRef.current.position.y = y;
    }
  });
  return (
    <mesh ref={meshRef} rotation={[Math.PI / 2, 0, 0]}>
      <planeGeometry args={[2.4, 2.4, 1, 1]} />
      <meshBasicMaterial color={'#00E5FF'} transparent opacity={0.12} blending={THREE.AdditiveBlending} />
    </mesh>
  );
}

function HologramCube() {
  const groupRef = useRef<THREE.Group>(null);
  useFrame((_, delta) => {
    if (groupRef.current) {
      groupRef.current.rotation.y += delta * 0.6;
    }
  });
  return (
    <group ref={groupRef}>
      <mesh>
        <boxGeometry args={[2, 2, 2, 24, 24, 24]} />
        {/* Glow/Fresnel + Scanlines */}
        <HologramMaterial />
      </mesh>
      {/* Wireframe-Rahmen für Cyber-Look */}
      <lineSegments>
        <edgesGeometry args={[new THREE.BoxGeometry(2, 2, 2)]} />
        <lineBasicMaterial color={'#00E5FF'} linewidth={1} transparent opacity={0.4} />
      </lineSegments>
      {/* Scan-Plane, die durch den Würfel fährt */}
      <ScanPlane />
    </group>
  );
}

function Particles({ count = 1500 }: { count?: number }) {
  const points = useRef<THREE.Points>(null);
  const positions = useMemo(() => {
    const arr = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      const i3 = i * 3;
      // Partikel in der Nähe des Würfels verteilen
      arr[i3 + 0] = (Math.random() - 0.5) * 6;
      arr[i3 + 1] = (Math.random() - 0.5) * 6;
      arr[i3 + 2] = (Math.random() - 0.5) * 6;
    }
    return arr;
  }, [count]);

  const velocities = useMemo(() => {
    const v = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      const i3 = i * 3;
      v[i3 + 0] = (Math.random() - 0.5) * 0.05;
      v[i3 + 1] = (Math.random() - 0.5) * 0.05;
      v[i3 + 2] = (Math.random() - 0.5) * 0.05;
    }
    return v;
  }, [count]);

  const sizes = useMemo(() => {
    const s = new Float32Array(count);
    for (let i = 0; i < count; i++) s[i] = Math.random() * 2 + 0.5;
    return s;
  }, [count]);

  useFrame((_, delta) => {
    const geo = points.current?.geometry as THREE.BufferGeometry | undefined;
    if (!geo) return;
    const pos = geo.getAttribute('position') as THREE.BufferAttribute;
    for (let i = 0; i < count; i++) {
      const i3 = i * 3;
      pos.array[i3 + 0] += velocities[i3 + 0];
      pos.array[i3 + 1] += velocities[i3 + 1];
      pos.array[i3 + 2] += velocities[i3 + 2];
      // sanftes Zurückziehen Richtung Zentrum
      pos.array[i3 + 0] *= 0.998;
      pos.array[i3 + 1] *= 0.998;
      pos.array[i3 + 2] *= 0.998;
    }
    pos.needsUpdate = true;
  });

  const geometry = useMemo(() => {
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    return g;
  }, [positions]);

  return (
    <points ref={points} geometry={geometry}>
      <pointsMaterial
        color={'#00E5FF'}
        size={0.05}
        sizeAttenuation
        depthWrite={false}
        transparent
        opacity={0.7}
        blending={THREE.AdditiveBlending}
      />
    </points>
  );
}

function BurstParticles({ capacity = 1000 }: { capacity?: number }) {
  const pointsRef = useRef<THREE.Points>(null);
  const consumeBurst = useHologramStore((s) => s.consumeBurst);

  const positions = useMemo(() => new Float32Array(capacity * 3), [capacity]);
  const velocities = useMemo(() => new Float32Array(capacity * 3), [capacity]);
  const life = useMemo(() => new Float32Array(capacity), [capacity]);

  const geometry = useMemo(() => {
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    return g;
  }, [positions]);

  const spawnBurst = (count: number) => {
    let spawned = 0;
    for (let i = 0; i < capacity && spawned < count; i++) {
      if (life[i] > 0) continue;
      const i3 = i * 3;
      // Start nahe Zentrum (innerhalb des Würfels)
      positions[i3 + 0] = (Math.random() - 0.5) * 0.4;
      positions[i3 + 1] = (Math.random() - 0.5) * 0.4;
      positions[i3 + 2] = (Math.random() - 0.5) * 0.4;
      // Richtung nach außen
      const dir = new THREE.Vector3(Math.random() - 0.5, Math.random() - 0.2, Math.random() - 0.5).normalize();
      const speed = 0.8 + Math.random() * 1.8;
      velocities[i3 + 0] = dir.x * speed;
      velocities[i3 + 1] = Math.abs(dir.y) * speed * 1.2; // leicht nach oben
      velocities[i3 + 2] = dir.z * speed;
      life[i] = 1.2 + Math.random() * 0.8; // Sekunden
      spawned++;
    }
    const posAttr = geometry.getAttribute('position') as THREE.BufferAttribute;
    posAttr.needsUpdate = true;
  };

  useFrame((_, delta) => {
    // Konsumiere Burst-Trigger
    const toSpawn = consumeBurst();
    if (toSpawn) spawnBurst(toSpawn);

    const posAttr = geometry.getAttribute('position') as THREE.BufferAttribute;
    for (let i = 0; i < capacity; i++) {
      const i3 = i * 3;
      if (life[i] > 0) {
        // Update
        positions[i3 + 0] += velocities[i3 + 0] * delta;
        positions[i3 + 1] += velocities[i3 + 1] * delta;
        positions[i3 + 2] += velocities[i3 + 2] * delta;
        // Dämpfung
        velocities[i3 + 0] *= 0.98;
        velocities[i3 + 1] = velocities[i3 + 1] * 0.98 - 0.3 * delta; // leichte Schwerkraft
        velocities[i3 + 2] *= 0.98;
        life[i] -= delta;
        if (life[i] <= 0) {
          // Verstecken
          positions[i3 + 0] = 9999;
          positions[i3 + 1] = 9999;
          positions[i3 + 2] = 9999;
        }
      }
    }
    posAttr.needsUpdate = true;
  });

  return (
    <points ref={pointsRef} geometry={geometry}>
      <pointsMaterial
        color={'#00E5FF'}
        size={0.06}
        sizeAttenuation
        depthWrite={false}
        transparent
        opacity={0.9}
        blending={THREE.AdditiveBlending}
      />
    </points>
  );
}

function Scene({ particleCount }: { particleCount?: number }) {
  return (
    <>
      <ambientLight intensity={0.1} />
      <pointLight position={[5, 5, 5]} intensity={0.6} />
      <HologramCube />
      <Particles count={particleCount} />
      <BurstParticles capacity={1200} />
      <OrbitControls enablePan={false} enableDamping dampingFactor={0.08} />
    </>
  );
}

const HologramScanner: React.FC<HologramScannerProps> = ({ className, style, particleCount = 1500 }) => {
  return (
    <div className={className} style={{ position: 'absolute', inset: 0, ...(style || {}) }}>
      <Canvas
        camera={{ position: [0, 0, 5], fov: 50 }}
        gl={{ antialias: true, powerPreference: 'high-performance' }}
        dpr={[1, 2]}
        frameloop="always"
      >
        <color attach="background" args={[0, 0, 0]} />
        <Scene particleCount={particleCount} />
        {/* Adaptive DPR für stabile 60 FPS */}
        <AdaptiveDpr pixelated />
        {/* Stärkerer Glow via Bloom */}
        <EffectComposer multisampling={0}>
          <Bloom
            luminanceThreshold={0.2}
            luminanceSmoothing={0.9}
            intensity={1.1}
          />
        </EffectComposer>
      </Canvas>
    </div>
  );
};

export default HologramScanner;

