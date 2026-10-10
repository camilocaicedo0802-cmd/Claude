import React, { useMemo } from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import * as THREE from "three";
import { RoundedBoxGeometry } from "three/examples/jsm/geometries/RoundedBoxGeometry.js";
import { TextGeometry } from "three/examples/jsm/geometries/TextGeometry.js";
import { FontLoader } from "three/examples/jsm/loaders/FontLoader.js";
import helvetiker from "three/examples/fonts/helvetiker_bold.typeface.json";
import { COLORS } from "../brand";
import { C, CLAMP, Clay, discoRedondeado, Escena, Props, suave, textura, useFuente } from "../rutinas/Objetos3D";

// Objetos 3D nuevos del día 10 "Día 21 y continuidad" (último del reto; clay mate y paleta Beleza). Todo se anima con
// el fotograma. Cada uno nace de su frase: globos metálicos "21" con estallido de estrellas ("llegaste al día 21",
// "un gran logro", "una rutina"), móvil en trípode que dispara ("te vas a tomar las fotos en las mismas posiciones"),
// maniquí con cinta métrica que se enrolla en los mismos puntos ("toma medidas… vuelve a revisar estas medidas"),
// corazón que late y se multiplica ("no puedes frustrarte", "puede motivar a otras mujeres"), semana con tres días
// marcados (cuadro: "calendario con dos o tres días señalados"), espejo de mano ("revisando cómo se va comportando tu
// piel") y globo de diálogo que escribe ("cuéntanos vía WhatsApp").

const MARFIL3D = "#E9D9C6";
const ORO = "#E4B373";
const useTAbs = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return frame / fps;
};
const FUENTE_3D = new FontLoader().parse(helvetiker as unknown as Parameters<FontLoader["parse"]>[0]);

// ---------- Estrella extruida (estallidos) ----------
const formaEstrella = (r1: number, r2: number) => {
  const s = new THREE.Shape();
  for (let i = 0; i < 10; i++) {
    const a = Math.PI / 2 + (i * Math.PI) / 5;
    const r = i % 2 ? r2 : r1;
    if (i === 0) s.moveTo(Math.cos(a) * r, Math.sin(a) * r);
    else s.lineTo(Math.cos(a) * r, Math.sin(a) * r);
  }
  s.closePath();
  return s;
};
const useEstrella = () =>
  useMemo(() => {
    const g = new THREE.ExtrudeGeometry(formaEstrella(0.2, 0.09), {
      depth: 0.05,
      bevelEnabled: true,
      bevelSize: 0.025,
      bevelThickness: 0.025,
      bevelSegments: 3,
    });
    g.center();
    return g;
  }, []);
const Estallido: React.FC<{ t: number; n?: number; radio?: number }> = ({ t, n = 9, radio = 1.9 }) => {
  const estrella = useEstrella();
  if (t < 0 || t > 1.4) return null;
  const k = suave(t / 0.9);
  return (
    <>
      {[...Array(n)].map((_, i) => {
        const a = (i / n) * Math.PI * 2 + 0.3;
        const r = radio * k;
        return (
          <mesh
            key={i}
            geometry={estrella}
            position={[Math.cos(a) * r, Math.sin(a) * r * 0.85, 0.4 + 0.3 * Math.sin(i)]}
            rotation={[0, t * 3, t * 4 + i]}
            scale={(1 - CLAMP((t - 0.7) / 0.7)) * (0.8 + 0.4 * (i % 3) / 2)}
          >
            <meshStandardMaterial
              color={i % 3 === 0 ? C.salvia : i % 3 === 1 ? ORO : C.durazno}
              emissive={C.durazno}
              emissiveIntensity={0.35}
              roughness={0.35}
              metalness={0.2}
            />
          </mesh>
        );
      })}
    </>
  );
};

// ---------- 1 · Globos metálicos "21": suben, flotan y estallan en estrellas ----------
export const Globos21: React.FC<Props & { fiesta?: number }> = ({ fiesta, ...props }) => {
  const digitos = useMemo(
    () =>
      ["2", "1"].map((d) => {
        const g = new TextGeometry(d, {
          font: FUENTE_3D,
          size: 1.5,
          depth: 0.28,
          curveSegments: 14,
          bevelEnabled: true,
          bevelThickness: 0.16,
          bevelSize: 0.09,
          bevelSegments: 6,
        });
        g.center();
        return g;
      }),
    [],
  );
  const tAbs = useTAbs();
  return (
    <Escena {...props} z={9}>
      {(p, t) => {
        const sube = suave(t / 0.9);
        return (
          <group scale={1.55 * (0.6 + 0.4 * p)} position={[0, -1.2 * (1 - sube) + 0.45, 0]}>
            {digitos.map((g, i) => {
              const x = i === 0 ? -0.62 : 0.72;
              const fase = i * 1.7;
              return (
                <group
                  key={i}
                  position={[x, Math.sin(t * 1.6 + fase) * 0.09, 0]}
                  rotation={[0.05, Math.sin(t * 0.9 + fase) * 0.35, Math.sin(t * 1.3 + fase) * 0.06]}
                >
                  <mesh geometry={g}>
                    <meshStandardMaterial color={i === 0 ? ORO : "#D9A05F"} roughness={0.22} metalness={0.45} />
                  </mesh>
                  {/* Cuerda */}
                  <mesh position={[0, -1.35, 0]}>
                    <cylinderGeometry args={[0.012, 0.012, 1.1, 6]} />
                    <meshStandardMaterial color={C.petroleo} />
                  </mesh>
                  <mesh position={[0, -0.82, 0]}>
                    <sphereGeometry args={[0.05, 12, 8]} />
                    <meshStandardMaterial color={ORO} />
                  </mesh>
                </group>
              );
            })}
            {fiesta !== undefined ? <Estallido t={tAbs - fiesta} /> : null}
          </group>
        );
      }}
    </Escena>
  );
};

// ---------- 2 · Móvil en trípode: "te vas a tomar las fotos en las mismas posiciones" → dispara con destello ----------
export const Celular3D: React.FC<Props & { dispara: number }> = ({ dispara, ...props }) => {
  const fuente = useFuente("700 80px 'Glacial Indifference'");
  const cuerpo = useMemo(() => new RoundedBoxGeometry(1.15, 2.2, 0.14, 4, 0.12), []);
  const pantalla = useMemo(
    () =>
      fuente
        ? textura(360, 680, (ctx) => {
            ctx.fillStyle = COLORS.marfil;
            ctx.fillRect(0, 0, 360, 680);
            ctx.strokeStyle = "rgba(69,89,90,.25)";
            ctx.lineWidth = 3;
            for (const k of [1, 2]) {
              ctx.beginPath();
              ctx.moveTo((360 * k) / 3, 60);
              ctx.lineTo((360 * k) / 3, 600);
              ctx.moveTo(0, 60 + (540 * k) / 3);
              ctx.lineTo(360, 60 + (540 * k) / 3);
              ctx.stroke();
            }
            // Silueta de pie (frente)
            ctx.fillStyle = C.salvia;
            ctx.beginPath();
            ctx.arc(180, 190, 42, 0, Math.PI * 2);
            ctx.fill();
            ctx.beginPath();
            ctx.moveTo(120, 250);
            ctx.quadraticCurveTo(180, 230, 240, 250);
            ctx.lineTo(250, 420);
            ctx.lineTo(225, 560);
            ctx.lineTo(195, 560);
            ctx.lineTo(180, 440);
            ctx.lineTo(165, 560);
            ctx.lineTo(135, 560);
            ctx.lineTo(110, 420);
            ctx.closePath();
            ctx.fill();
            ctx.fillStyle = C.petroleo;
            ctx.fillRect(0, 0, 360, 56);
            ctx.fillStyle = COLORS.marfil;
            ctx.font = "700 30px 'Glacial Indifference'";
            ctx.textAlign = "center";
            ctx.fillText("DÍA 21", 180, 39);
            ctx.fillStyle = C.petroleo;
            ctx.beginPath();
            ctx.arc(180, 640, 26, 0, Math.PI * 2);
            ctx.fill();
          })
        : null,
    [fuente],
  );
  const tAbs = useTAbs();
  return (
    <Escena {...props} z={9}>
      {(p, t) => {
        const d = tAbs - dispara;
        const flash = d > 0 && d < 0.35 ? 1 - d / 0.35 : 0;
        return (
          <group scale={1.5 * (0.6 + 0.4 * p)} position={[0, -0.08, 0]} rotation={[0.1, -0.6 + Math.sin(t * 0.8) * 0.25, 0]}>
            <group position={[0, 0.45, 0]}>
              <mesh geometry={cuerpo}>
                <Clay color={C.petroleo} />
              </mesh>
              {pantalla ? (
                <mesh position={[0, 0, 0.075]}>
                  <planeGeometry args={[1.0, 1.9]} />
                  <meshStandardMaterial map={pantalla} roughness={0.5} emissive="#FFFFFF" emissiveIntensity={0.15 + flash * 1.2} />
                </mesh>
              ) : null}
              {/* Pinza del trípode */}
              <mesh position={[0, -1.16, -0.05]}>
                <boxGeometry args={[0.5, 0.14, 0.2]} />
                <Clay color={C.durazno} />
              </mesh>
            </group>
            {/* Trípode corto: tres patas que salen de la rótula */}
            <mesh position={[0, -0.84, -0.05]}>
              <sphereGeometry args={[0.1, 16, 12]} />
              <Clay color={C.durazno} />
            </mesh>
            {[0, 1, 2].map((i) => (
              <group key={i} position={[0, -0.84, -0.05]} rotation={[0, (i * 2 * Math.PI) / 3 + 0.5, 0]}>
                <group rotation={[0.42, 0, 0]}>
                  <mesh position={[0, -0.34, 0]}>
                    <cylinderGeometry args={[0.04, 0.03, 0.68, 10]} />
                    <Clay color={C.salvia} />
                  </mesh>
                </group>
              </group>
            ))}
            {/* Destello del disparo */}
            {flash > 0 ? (
              <mesh position={[0, 0.45, 0.3]} scale={1 + (1 - flash) * 1.5}>
                <ringGeometry args={[0.9, 1.05, 48]} />
                <meshBasicMaterial color="#FFFFFF" transparent opacity={flash} />
              </mesh>
            ) : null}
          </group>
        );
      }}
    </Escena>
  );
};

// ---------- 3 · Maniquí con cinta métrica: la cinta se enrolla en la cintura y luego en la cadera ----------
const PERFIL = new THREE.SplineCurve(
  [
    [0.001, -1.05],
    [0.6, -1.02],
    [0.84, -0.7],
    [0.8, -0.42],
    [0.64, -0.02],
    [0.62, 0.18],
    [0.72, 0.5],
    [0.82, 0.82],
    [0.8, 1.05],
    [0.55, 1.25],
    [0.25, 1.36],
    [0.24, 1.52],
    [0.001, 1.55],
  ].map(([r, y]) => new THREE.Vector2(r, y)),
).getPoints(80);
const radio = (y: number) => {
  for (let i = 1; i < PERFIL.length; i++) {
    const a = PERFIL[i - 1];
    const b = PERFIL[i];
    if ((y - a.y) * (y - b.y) <= 0) return a.x + ((b.x - a.x) * (y - a.y)) / (b.y - a.y || 1);
  }
  return 0.6;
};
const PASOS_CINTA = 40;
export const CintaManiqui3D: React.FC<Props & { cintura: number; cadera: number }> = ({ cintura, cadera, ...props }) => {
  const fuente = useFuente("700 80px 'Glacial Indifference'");
  const cuerpo = useMemo(() => new THREE.LatheGeometry(PERFIL, 64), []);
  const marcas = useMemo(
    () =>
      fuente
        ? textura(1024, 64, (ctx) => {
            ctx.fillStyle = "#F3CFA0";
            ctx.fillRect(0, 0, 1024, 64);
            ctx.fillStyle = C.petroleo;
            for (let i = 0; i <= 100; i++) {
              const x = (i / 100) * 1024;
              ctx.fillRect(x, 0, 2, i % 10 === 0 ? 30 : i % 5 === 0 ? 20 : 12);
              if (i % 10 === 0 && i < 100) {
                ctx.font = "700 22px 'Glacial Indifference'";
                ctx.fillText(String(i), x + 4, 56);
              }
            }
          })
        : null,
    [fuente],
  );
  // Cinta como cilindro abierto cuyo ángulo crece (geometrías precalculadas por pasos)
  const cintas = useMemo(
    () =>
      [-0.0, -0.62].map((y) => {
        const r = radio(y) * 1.03;
        return [...Array(PASOS_CINTA + 1)].map((_, k) =>
          new THREE.CylinderGeometry(r, r, 0.13, 64, 1, true, Math.PI / 2, Math.max(0.001, (k / PASOS_CINTA) * Math.PI * 2)),
        );
      }),
    [],
  );
  const tAbs = useTAbs();
  return (
    <Escena {...props} z={9.5}>
      {(p, t) => {
        const ks = [suave((tAbs - cintura) / 0.8), suave((tAbs - cadera) / 0.8)];
        return (
          <group scale={1.25 * (0.6 + 0.4 * p)} position={[0, 0.2, 0]} rotation={[0.1, Math.sin(t * 0.7) * 0.4, 0]}>
            <group scale={[1.1, 1, 0.75]}>
              <mesh geometry={cuerpo}>
                <Clay color={MARFIL3D} />
              </mesh>
              {cintas.map((pasos, i) => {
                const k = Math.round(ks[i] * PASOS_CINTA);
                if (k <= 0) return null;
                return (
                  <mesh key={i} geometry={pasos[k]} position={[0, i === 0 ? 0 : -0.62, 0]}>
                    <meshStandardMaterial map={marcas ?? undefined} color={marcas ? "#FFFFFF" : "#F3CFA0"} roughness={0.6} side={THREE.DoubleSide} />
                  </mesh>
                );
              })}
            </group>
            {/* Mismos puntos: chinchetas en cada medida cuando la cinta se cierra */}
            {[0, -0.62].map((y, i) =>
              ks[i] >= 1 ? (
                <mesh key={y} position={[0, y, radio(y) * 0.75 + 0.06]}>
                  <sphereGeometry args={[0.07, 16, 12]} />
                  <Clay color={C.petroleo} />
                </mesh>
              ) : null,
            )}
            <mesh position={[0, 1.6, 0]}>
              <sphereGeometry args={[0.14, 20, 14]} />
              <Clay color={C.petroleo} />
            </mesh>
            <mesh position={[0, -1.4, 0]}>
              <cylinderGeometry args={[0.055, 0.055, 0.7, 12]} />
              <Clay color={C.petroleo} />
            </mesh>
            <mesh position={[0, -1.78, 0]}>
              <cylinderGeometry args={[0.5, 0.56, 0.09, 36]} />
              <Clay color={C.petroleo} />
            </mesh>
          </group>
        );
      }}
    </Escena>
  );
};

// ---------- 4 · Corazón que late (y, si se pide, se multiplica en corazones más pequeños) ----------
const formaCorazon = () => {
  const s = new THREE.Shape();
  s.moveTo(0, -0.9);
  s.bezierCurveTo(-0.15, -0.72, -1.05, -0.2, -1.05, 0.32);
  s.bezierCurveTo(-1.05, 0.82, -0.45, 1.02, 0, 0.6);
  s.bezierCurveTo(0.45, 1.02, 1.05, 0.82, 1.05, 0.32);
  s.bezierCurveTo(1.05, -0.2, 0.15, -0.72, 0, -0.9);
  return s;
};
export const Corazon3D: React.FC<Props & { multiplica?: number; color?: string }> = ({ multiplica, color = C.durazno, ...props }) => {
  const geo = useMemo(() => {
    const g = new THREE.ExtrudeGeometry(formaCorazon(), {
      depth: 0.28,
      bevelEnabled: true,
      bevelSize: 0.14,
      bevelThickness: 0.16,
      bevelSegments: 8,
      curveSegments: 24,
    });
    g.center();
    return g;
  }, []);
  const tAbs = useTAbs();
  return (
    <Escena {...props} z={9}>
      {(p, t) => {
        // Latido doble cada 1,1 s
        const c = t % 1.1;
        const lat = 1 + 0.09 * Math.exp(-((c - 0.1) ** 2) / 0.004) + 0.06 * Math.exp(-((c - 0.32) ** 2) / 0.004);
        const m = multiplica === undefined ? 0 : suave((tAbs - multiplica) / 0.8);
        return (
          <group scale={1.6 * (0.6 + 0.4 * p)} rotation={[0.1, Math.sin(t * 0.9) * 0.35, 0]}>
            <mesh geometry={geo} scale={lat * (1 - 0.3 * m)}>
              <Clay color={color} rough={0.5} />
            </mesh>
            {m > 0
              ? [0, 1, 2, 3].map((i) => {
                  const a = (i / 4) * Math.PI * 2 + t * 0.8;
                  const r = 1.55 * m;
                  return (
                    <mesh
                      key={i}
                      geometry={geo}
                      position={[Math.cos(a) * r, Math.sin(a) * r * 0.8, 0.2]}
                      scale={0.32 * m * lat}
                      rotation={[0, t * 1.5 + i, 0]}
                    >
                      <Clay color={i % 2 ? C.salvia : C.durazno} rough={0.5} />
                    </mesh>
                  );
                })
              : null}
          </group>
        );
      }}
    </Escena>
  );
};

// ---------- 5 · Semana: siete fichas L–D; en "marca" se levantan tres (cuadro: "dos o tres días señalados") ----------
const DIAS = ["L", "M", "X", "J", "V", "S", "D"];
const MARCADOS = [0, 2, 4];
export const Semana3D: React.FC<Props & { marca: number }> = ({ marca, ...props }) => {
  const fuente = useFuente("700 80px 'Glacial Indifference'");
  const ficha = useMemo(() => new RoundedBoxGeometry(0.46, 0.58, 0.16, 4, 0.06), []);
  const letras = useMemo(
    () =>
      fuente
        ? DIAS.map((d) =>
            [false, true].map((on) =>
              textura(128, 160, (ctx) => {
                ctx.fillStyle = on ? C.salvia : COLORS.marfil;
                ctx.fillRect(0, 0, 128, 160);
                ctx.fillStyle = on ? COLORS.marfil : C.petroleo;
                ctx.textAlign = "center";
                ctx.textBaseline = "middle";
                ctx.font = "700 84px 'Glacial Indifference'";
                ctx.fillText(d, 64, on ? 64 : 84);
                if (on) {
                  ctx.strokeStyle = COLORS.marfil;
                  ctx.lineWidth = 10;
                  ctx.lineCap = "round";
                  ctx.beginPath();
                  ctx.moveTo(40, 126);
                  ctx.lineTo(58, 142);
                  ctx.lineTo(90, 112);
                  ctx.stroke();
                }
              }),
            ),
          )
        : null,
    [fuente],
  );
  const tAbs = useTAbs();
  return (
    <Escena {...props} z={9}>
      {(p, t) => (
        <group scale={2.05 * (0.6 + 0.4 * p)} rotation={[0.3, Math.sin(t * 0.7) * 0.18, 0]}>
          <mesh position={[0, 0, -0.14]}>
            <boxGeometry args={[2.3, 1.55, 0.08]} />
            <Clay color={C.durazno} />
          </mesh>
          {DIAS.map((d, i) => {
            const idx = MARCADOS.indexOf(i);
            const k = idx >= 0 ? suave((tAbs - marca - idx * 0.22) / 0.35) : 0;
            const fila = i < 4 ? 0 : 1;
            const x = fila === 0 ? (i - 1.5) * 0.52 : (i - 4 - 1) * 0.52;
            const y = fila === 0 ? 0.35 : -0.35;
            return (
              <group key={d} position={[x, y + 0.08 * k, 0.32 * k]} rotation={[-0.3 * k, 0, 0]}>
                <mesh geometry={ficha}>
                  <Clay color={k > 0.5 ? C.salvia : MARFIL3D} />
                </mesh>
                {letras ? (
                  <mesh position={[0, 0, 0.085]}>
                    <planeGeometry args={[0.38, 0.48]} />
                    <meshStandardMaterial map={letras[i][k > 0.5 ? 1 : 0]} roughness={0.7} />
                  </mesh>
                ) : null}
              </group>
            );
          })}
        </group>
      )}
    </Escena>
  );
};

// ---------- 6 · Espejo de mano: "revisando cómo se va comportando tu piel" → un brillo cruza el espejo ----------
export const Espejo3D: React.FC<Props> = (props) => {
  const marco = useMemo(() => discoRedondeado(0.98, 0.16, 0.06), []);
  return (
    <Escena {...props} z={9}>
      {(p, t) => (
        <group scale={1.45 * (0.6 + 0.4 * p)} position={[0, 0.55, 0]} rotation={[0.1, -0.4 + Math.sin(t * 0.8) * 0.35, 0.25]}>
          <mesh geometry={marco} rotation={[Math.PI / 2, 0, 0]}>
            <Clay color={C.durazno} />
          </mesh>
          <mesh position={[0, 0, 0.085]}>
            <circleGeometry args={[0.82, 64]} />
            <meshStandardMaterial color="#DCE8E6" roughness={0.06} metalness={0.9} />
          </mesh>
          <mesh position={[-0.9 + ((t * 0.8) % 1.8), 0, 0.09]} rotation={[0, 0, Math.PI / 4]}>
            <planeGeometry args={[0.14, 1.5]} />
            <meshBasicMaterial color="#FFFFFF" transparent opacity={0.55} />
          </mesh>
          <mesh position={[0, -1.45, 0]}>
            <cylinderGeometry args={[0.12, 0.15, 1.05, 20]} />
            <Clay color={C.petroleo} />
          </mesh>
          <mesh position={[0, -0.95, 0]}>
            <sphereGeometry args={[0.17, 20, 14]} />
            <Clay color={C.salvia} />
          </mesh>
        </group>
      )}
    </Escena>
  );
};

// ---------- 7 · Globo de diálogo: "cuéntanos" → tres puntos que escriben ----------
const formaGlobo = () => {
  const s = new THREE.Shape();
  const w = 1.5;
  const h = 1.0;
  const r = 0.38;
  s.moveTo(-w + r, -h);
  s.lineTo(-0.55, -h);
  s.lineTo(-0.85, -h - 0.42);
  s.lineTo(-0.2, -h);
  s.lineTo(w - r, -h);
  s.quadraticCurveTo(w, -h, w, -h + r);
  s.lineTo(w, h - r);
  s.quadraticCurveTo(w, h, w - r, h);
  s.lineTo(-w + r, h);
  s.quadraticCurveTo(-w, h, -w, h - r);
  s.lineTo(-w, -h + r);
  s.quadraticCurveTo(-w, -h, -w + r, -h);
  return s;
};
export const Dialogo3D: React.FC<Props> = (props) => {
  const geo = useMemo(() => {
    const g = new THREE.ExtrudeGeometry(formaGlobo(), {
      depth: 0.22,
      bevelEnabled: true,
      bevelSize: 0.1,
      bevelThickness: 0.12,
      bevelSegments: 6,
      curveSegments: 16,
    });
    g.center();
    return g;
  }, []);
  return (
    <Escena {...props} z={9}>
      {(p, t) => (
        <group scale={1.35 * (0.6 + 0.4 * p)} rotation={[0.12, -0.3 + Math.sin(t * 0.9) * 0.25, 0]} position={[0, Math.sin(t * 1.8) * 0.06, 0]}>
          <mesh geometry={geo}>
            <Clay color={C.salvia} />
          </mesh>
          {[-0.62, 0, 0.62].map((x, i) => (
            <mesh key={i} position={[x, 0.14 + Math.max(0, Math.sin(t * 7 - i * 0.9)) * 0.22, 0.3]}>
              <sphereGeometry args={[0.2, 20, 14]} />
              <Clay color={COLORS.marfil} />
            </mesh>
          ))}
        </group>
      )}
    </Escena>
  );
};
