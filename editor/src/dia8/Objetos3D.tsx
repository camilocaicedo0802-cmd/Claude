import React, { useMemo } from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import * as THREE from "three";
import { RoundedBoxGeometry } from "three/examples/jsm/geometries/RoundedBoxGeometry.js";
import {
  C,
  CLAMP,
  Clay,
  discoRedondeado,
  Escena,
  Props,
  suave,
  textura,
  useFuente,
} from "../rutinas/Objetos3D";

// Objetos 3D nuevos del día 8 "Evaluación del Día 10" (clay mate, paleta Beleza). Todo se anima con el fotograma.

const useTAbs = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return frame / fps;
};

// ---------- Calendario: "llegaste al día 10" → las hojas pasan 7·8·9 hasta el 10 y se marca con un check ----------
const PAGINAS = [7, 8, 9, 10];
export const Calendario3D: React.FC<
  Props & { diez: number; marca: number }
> = ({ diez, marca, ...props }) => {
  const fuente = useFuente("700 80px 'Glacial Indifference'");
  const cuerpo = useMemo(
    () => new RoundedBoxGeometry(2.3, 2.5, 0.28, 5, 0.12),
    [],
  );
  const barra = useMemo(
    () => new RoundedBoxGeometry(2.4, 0.5, 0.4, 5, 0.16),
    [],
  );
  const hojas = useMemo(
    () =>
      fuente
        ? PAGINAS.map((n) =>
            textura(512, 512, (ctx) => {
              ctx.fillStyle = C.marfil;
              ctx.fillRect(0, 0, 512, 512);
              ctx.fillStyle = C.salvia;
              ctx.textAlign = "center";
              ctx.textBaseline = "middle";
              ctx.font = "700 64px 'Glacial Indifference'";
              ctx.fillText("DÍA", 256, 110);
              ctx.fillStyle = C.petroleo;
              ctx.font = "700 260px 'Glacial Indifference'";
              ctx.fillText(String(n), 256, 300);
              ctx.font = "400 40px 'Glacial Indifference'";
              ctx.fillStyle = C.salvia;
              ctx.fillText("DE 21", 256, 455);
            }),
          )
        : null,
    [fuente],
  );
  const tAbs = useTAbs();
  return (
    <Escena {...props} z={9}>
      {(p, t) => {
        // Cada hoja cae girando sobre la barra; la última (10) se queda
        const pasa = (i: number) => {
          const t0 = diez - (PAGINAS.length - 1 - i) * 0.22 - 0.22;
          return suave((tAbs - t0) / 0.22);
        };
        const dm = CLAMP((tAbs - marca) / 0.3);
        return (
          <group
            scale={1.15 * (0.55 + 0.45 * p)}
            rotation={[0.18, -0.35 + Math.sin(t * 1.0) * 0.18, 0.04]}
          >
            <mesh geometry={cuerpo} position={[0, -0.1, -0.12]}>
              <Clay color={C.durazno} />
            </mesh>
            {hojas
              ? PAGINAS.map((n, i) => {
                  const g = i < PAGINAS.length - 1 ? pasa(i) : 0;
                  if (g >= 1) return null;
                  return (
                    <group
                      key={n}
                      position={[0, 1.0, 0.04 + (PAGINAS.length - i) * 0.004]}
                      rotation={[-g * Math.PI * 0.95, 0, 0]}
                    >
                      <mesh position={[0, -1.08, 0]}>
                        <planeGeometry args={[2.05, 2.1]} />
                        <meshStandardMaterial
                          map={hojas[i]}
                          roughness={0.85}
                          side={THREE.DoubleSide}
                        />
                      </mesh>
                    </group>
                  );
                })
              : null}
            <mesh geometry={barra} position={[0, 1.15, 0.05]}>
              <Clay color={C.petroleo} />
            </mesh>
            {[-0.6, 0.6].map((x) => (
              <mesh
                key={x}
                position={[x, 1.42, 0.08]}
                rotation={[0, Math.PI / 2, 0]}
              >
                <torusGeometry args={[0.2, 0.06, 12, 32]} />
                <Clay color={C.salvia} />
              </mesh>
            ))}
            {/* Check que se estampa sobre el 10 */}
            {dm > 0 ? (
              <group
                position={[0.62, -0.62, 0.25]}
                scale={0.3 + 0.7 * dm + 0.15 * Math.sin(dm * Math.PI)}
              >
                <mesh>
                  <circleGeometry args={[0.46, 40]} />
                  <meshStandardMaterial color={C.salvia} roughness={0.5} />
                </mesh>
                <mesh position={[-0.11, -0.04, 0.02]} rotation={[0, 0, 0.8]}>
                  <boxGeometry args={[0.1, 0.28, 0.04]} />
                  <meshStandardMaterial color={C.marfil} />
                </mesh>
                <mesh position={[0.08, 0.05, 0.02]} rotation={[0, 0, -0.65]}>
                  <boxGeometry args={[0.1, 0.48, 0.04]} />
                  <meshStandardMaterial color={C.marfil} />
                </mesh>
              </group>
            ) : null}
          </group>
        );
      }}
    </Escena>
  );
};

// ---------- Pausa: "determina si es necesario suspender" → botón de pausa que se hunde y late ----------
export const Pausa3D: React.FC<Props & { pulsa: number }> = ({
  pulsa,
  ...props
}) => {
  const base = useMemo(() => discoRedondeado(1.3, 0.36, 0.14), []);
  const barra = useMemo(
    () => new RoundedBoxGeometry(0.32, 1.05, 0.3, 4, 0.12),
    [],
  );
  const tAbs = useTAbs();
  const d = tAbs - pulsa;
  const hunde = d > 0 ? Math.sin(CLAMP(d / 0.35) * Math.PI) : 0;
  return (
    <Escena {...props}>
      {(p, t) => (
        <group
          scale={1.3 * (0.55 + 0.45 * p)}
          rotation={[0.3, -0.3 + Math.sin(t * 1.1) * 0.15, 0]}
        >
          <mesh geometry={base} rotation={[Math.PI / 2, 0, 0]}>
            <Clay color={C.petroleo} />
          </mesh>
          {[-0.3, 0.3].map((x) => (
            <mesh
              key={x}
              geometry={barra}
              position={[x, 0, 0.3 - hunde * 0.15]}
            >
              <meshStandardMaterial
                color={C.durazno}
                emissive={C.durazno}
                emissiveIntensity={d > 0 ? 0.25 + 0.15 * Math.sin(t * 5) : 0}
                roughness={0.55}
              />
            </mesh>
          ))}
        </group>
      )}
    </Escena>
  );
};

// ---------- Tarro de crema: "o por una crema más suave" → la tapa se levanta y sale una crema suave ----------
const tarroGeom = () => {
  const pts = [
    [0, -0.75],
    [0.95, -0.75],
    [1.05, -0.65],
    [1.08, 0.35],
    [0.98, 0.45],
    [0, 0.45],
  ].map(([x, y]) => new THREE.Vector2(x, y));
  return new THREE.LatheGeometry(pts, 64);
};
export const Crema3D: React.FC<Props & { abre: number }> = ({
  abre,
  ...props
}) => {
  const fuente = useFuente("700 80px 'Glacial Indifference'");
  const tarro = useMemo(tarroGeom, []);
  const tapa = useMemo(() => discoRedondeado(1.12, 0.36, 0.12), []);
  const etiqueta = useMemo(
    () =>
      fuente
        ? textura(1024, 256, (ctx) => {
            ctx.fillStyle = C.marfil;
            ctx.fillRect(0, 0, 1024, 256);
            ctx.fillStyle = C.salvia;
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";
            ctx.font = "700 92px 'Glacial Indifference'";
            ctx.fillText("CREMA SUAVE", 512, 128);
          })
        : null,
    [fuente],
  );
  const tAbs = useTAbs();
  const a = suave((tAbs - abre) / 0.6);
  return (
    <Escena {...props}>
      {(p, t) => (
        <group
          scale={1.3 * (0.6 + 0.4 * p)}
          rotation={[0.42, -0.4 + Math.sin(t * 0.9) * 0.2, 0]}
          position={[0, -0.25, 0]}
        >
          <mesh geometry={tarro}>
            <Clay color={C.marfil} rough={0.5} />
          </mesh>
          {etiqueta ? (
            <mesh position={[0, -0.15, 0]} rotation={[0, -Math.PI / 2, 0]}>
              <cylinderGeometry args={[1.09, 1.09, 0.55, 64, 1, true]} />
              <meshStandardMaterial
                map={etiqueta}
                roughness={0.7}
                side={THREE.DoubleSide}
              />
            </mesh>
          ) : null}
          {/* Crema: cúpula durazno con un remolino */}
          <mesh position={[0, 0.45, 0]} scale={[0.95, 0.35 + 0.15 * a, 0.95]}>
            <sphereGeometry
              args={[1, 40, 20, 0, Math.PI * 2, 0, Math.PI / 2]}
            />
            <Clay color={C.durazno} rough={0.4} />
          </mesh>
          <mesh
            position={[0, 0.62 + 0.08 * a, 0]}
            rotation={[Math.PI / 2, 0, t]}
          >
            <torusGeometry args={[0.32, 0.07, 12, 40]} />
            <Clay color="#F7E0BC" rough={0.4} />
          </mesh>
          {/* Tapa que se levanta y se aparta */}
          <group
            position={[a * 1.25, 0.65 + a * 0.9, -a * 0.3]}
            rotation={[0, 0, -a * 0.7]}
          >
            <mesh geometry={tapa} rotation={[0, 0, 0]}>
              <Clay color={C.salvia} />
            </mesh>
          </group>
        </group>
      )}
    </Escena>
  );
};
