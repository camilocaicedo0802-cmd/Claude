import React from 'react';
import {ThreeCanvas} from '@remotion/three';
import {C} from '../theme';

const Ring: React.FC<{r: number; len: number; z: number; color: string; metal?: number; rough?: number; seg?: number}> = ({
  r,
  len,
  z,
  color,
  metal = 0.3,
  rough = 0.45,
  seg = 64,
}) => (
  <mesh position={[0, 0, z]} rotation={[Math.PI / 2, 0, 0]}>
    <cylinderGeometry args={[r, r, len, seg]} />
    <meshStandardMaterial color={color} metalness={metal} roughness={rough} />
  </mesh>
);

/** Cámara de cine/foto profesional construida con primitivas 3D (cuerpo, grip, visor, objetivo con anillos). */
const CameraModel: React.FC<{ry: number; rx: number; rz: number}> = ({ry, rx, rz}) => {
  const body = '#2E2D35';
  return (
    <group rotation={[rx, ry, rz]}>
      {/* cuerpo */}
      <mesh>
        <boxGeometry args={[2.6, 1.6, 1.05]} />
        <meshStandardMaterial color={body} roughness={0.55} metalness={0.25} />
      </mesh>
      {/* grip */}
      <mesh position={[-1.05, -0.05, 0.25]}>
        <boxGeometry args={[0.62, 1.55, 1.25]} />
        <meshStandardMaterial color="#121115" roughness={0.85} metalness={0.05} />
      </mesh>
      {/* prisma / visor */}
      <mesh position={[0.1, 1.0, -0.05]}>
        <boxGeometry args={[0.95, 0.5, 0.85]} />
        <meshStandardMaterial color={body} roughness={0.5} metalness={0.3} />
      </mesh>
      <mesh position={[0.1, 1.28, -0.05]}>
        <boxGeometry args={[0.5, 0.08, 0.4]} />
        <meshStandardMaterial color="#555" roughness={0.3} metalness={0.9} />
      </mesh>
      {/* diales */}
      <mesh position={[-0.85, 0.9, -0.1]}>
        <cylinderGeometry args={[0.24, 0.24, 0.18, 40]} />
        <meshStandardMaterial color="#2C2B31" roughness={0.4} metalness={0.6} />
      </mesh>
      <mesh position={[0.95, 0.88, 0]}>
        <cylinderGeometry args={[0.2, 0.2, 0.14, 40]} />
        <meshStandardMaterial color="#2C2B31" roughness={0.4} metalness={0.6} />
      </mesh>
      {/* botón REC */}
      <mesh position={[-0.95, 0.83, 0.4]}>
        <cylinderGeometry args={[0.08, 0.08, 0.06, 24]} />
        <meshStandardMaterial color="#FF3355" emissive="#FF3355" emissiveIntensity={0.6} />
      </mesh>
      {/* objetivo */}
      <group position={[0.15, -0.05, 0.52]}>
        <Ring r={0.7} len={0.14} z={0.07} color="#9A9AA2" metal={0.95} rough={0.25} />
        <Ring r={0.64} len={0.55} z={0.4} color="#141317" rough={0.6} />
        <Ring r={0.68} len={0.38} z={0.85} color="#2A2930" rough={0.9} seg={36} />
        <Ring r={0.66} len={0.5} z={1.28} color="#141317" rough={0.5} />
        <Ring r={0.67} len={0.05} z={1.1} color={C.cardLight} metal={0.4} rough={0.3} />
        <Ring r={0.72} len={0.12} z={1.58} color="#1E1D22" rough={0.4} metal={0.5} />
        <mesh position={[0, 0, 1.645]} rotation={[Math.PI / 2, 0, 0]}>
          <cylinderGeometry args={[0.56, 0.56, 0.02, 64]} />
          <meshPhysicalMaterial color="#1A0F2A" metalness={0.9} roughness={0.06} clearcoat={1} emissive="#3B1A52" emissiveIntensity={0.35} />
        </mesh>
        <mesh position={[0.18, 0.2, 1.66]} rotation={[Math.PI / 2, 0, 0]}>
          <cylinderGeometry args={[0.12, 0.12, 0.01, 32]} />
          <meshBasicMaterial color="#B990D0" transparent opacity={0.55} />
        </mesh>
      </group>
    </group>
  );
};

export const Camera3D: React.FC<{w: number; h: number; ry: number; rx?: number; rz?: number; scale?: number}> = ({
  w,
  h,
  ry,
  rx = 0.18,
  rz = 0,
  scale = 1,
}) => (
  <ThreeCanvas width={w} height={h} camera={{fov: 30, position: [0, 0.4, 9.5]}} gl={{antialias: true, alpha: true, preserveDrawingBuffer: true}}>
    <ambientLight intensity={1.1} />
    <hemisphereLight args={['#ffffff', '#3b1a52', 1.2]} />
    <directionalLight position={[4, 5, 6]} intensity={3.4} />
    <directionalLight position={[-5, 2, -3]} intensity={1.4} color={'#B57CD0'} />
    <pointLight position={[-3, -2, 4]} intensity={18} color={'#714181'} decay={1.2} />
    <group scale={scale}>
      <CameraModel ry={ry} rx={rx} rz={rz} />
    </group>
  </ThreeCanvas>
);
