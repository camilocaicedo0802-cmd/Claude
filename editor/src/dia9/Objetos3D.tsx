import React, { useMemo } from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import * as THREE from "three";
import { RoundedBoxGeometry } from "three/examples/jsm/geometries/RoundedBoxGeometry.js";
import { COLORS, FONTS } from "../brand";
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

// Objetos 3D nuevos del día 9 "Rutina integrada" (clay mate, paleta Beleza). Todo se anima con el fotograma.
// Cada uno nace de su frase: rompecabezas ("integraremos diferentes zonas en una sola rutina"), gota que se queda
// dentro de la zona ("únicamente en la zona… deslizamiento"), reloj de arena ("3 minutos"), chevrones ("líneas
// ascendentes"), maniquí de torso (abdomen, laterales, ombligo, círculos, arrastre), medidor ("intensidad baja",
// "sin… intensidad dolorosa"), espiral ("movimientos circulares y barridos ascendentes"), reloj de tarjetas 00:30
// ("30 segundos") y medalla ("rutina completa de 15 minutos").

const MARFIL3D = "#E9D9C6"; // con la luz de estudio el #F5F0EC se ve blanco
const useTAbs = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return frame / fps;
};

/** Objeto 3D con su rótulo (píldora) debajo, en una sola caja para la maqueta de columnas. */
export const ConRotulo: React.FC<{
  ancho: number;
  alto: number;
  rotulo?: string;
  rotuloAt?: number;
  style?: React.CSSProperties;
  children: React.ReactNode;
}> = ({ ancho, alto, rotulo, rotuloAt = 0, style, children }) => {
  const t = useTAbs();
  const p = suave((t - rotuloAt) / 0.3);
  return (
    <div
      style={{
        position: "absolute",
        width: ancho,
        height: alto + (rotulo ? 56 : 0),
        ...style,
      }}
    >
      {children}
      {rotulo && p > 0 ? (
        <div
          style={{
            position: "absolute",
            top: alto - 6,
            left: 0,
            right: 0,
            display: "flex",
            justifyContent: "center",
            opacity: p,
            transform: `translateY(${(1 - p) * 16}px)`,
          }}
        >
          <div
            style={{
              fontFamily: FONTS.body,
              fontWeight: 700,
              fontSize: 24,
              letterSpacing: "0.14em",
              color: COLORS.petroleo,
              background: COLORS.durazno,
              borderRadius: 30,
              padding: "9px 20px 7px",
              boxShadow: "0 8px 22px rgba(69,89,90,.3)",
              whiteSpace: "nowrap",
            }}
          >
            {rotulo}
          </div>
        </div>
      ) : null}
    </div>
  );
};

// ---------- 1 · Rompecabezas: las 4 zonas encajan en "una sola rutina" ----------
const PIEZAS = [
  { zona: "piernas", color: C.salvia, tinta: COLORS.marfil, x: -1, y: 1, tabs: ["der", "aba"] },
  { zona: "abdomen", color: C.durazno, tinta: COLORS.petroleo, x: 1, y: 1, tabs: ["aba"] },
  { zona: "glúteos", color: C.petroleo, tinta: COLORS.durazno, x: -1, y: -1, tabs: ["der"] },
  { zona: "brazos", color: MARFIL3D, tinta: COLORS.petroleo, x: 1, y: -1, tabs: [] },
];
export const Rompecabezas3D: React.FC<Props & { encaja: number }> = ({
  encaja,
  ...props
}) => {
  const fuente = useFuente("700 80px 'Glacial Indifference'");
  const caja = useMemo(() => new RoundedBoxGeometry(1.0, 1.0, 0.32, 4, 0.07), []);
  const caras = useMemo(
    () =>
      fuente
        ? PIEZAS.map((pz) =>
            textura(512, 512, (ctx) => {
              ctx.fillStyle = pz.color;
              ctx.fillRect(0, 0, 512, 512);
              ctx.fillStyle = pz.tinta;
              ctx.textAlign = "center";
              ctx.textBaseline = "middle";
              ctx.font = "700 92px 'Glacial Indifference'";
              ctx.fillText(pz.zona.toUpperCase(), 256, 262);
            }),
          )
        : null,
    [fuente],
  );
  const tAbs = useTAbs();
  return (
    <Escena {...props} z={9}>
      {(p, t) => {
        const tras = tAbs - encaja;
        const pulso = tras > 0 ? Math.sin(tras * 9) * Math.exp(-tras * 3) * 0.06 : 0;
        return (
          <group
            scale={1.45 * (0.6 + 0.4 * p) * (1 + pulso)}
            rotation={[0.25, -0.35 + Math.sin(t * 0.9) * 0.2, 0.05]}
          >
            {PIEZAS.map((pz, i) => {
              const k = suave((tAbs - (encaja - 0.62 + i * 0.12)) / 0.42);
              const dx = pz.x * 0.52;
              const dy = pz.y * 0.52;
              return (
                <group
                  key={pz.zona}
                  position={[
                    dx + pz.x * 0.8 * (1 - k),
                    dy + pz.y * 0.7 * (1 - k),
                    (1 - k) * (i % 2 ? -1.5 : -2.5),
                  ]}
                  rotation={[0, (1 - k) * 0.9 * pz.x, (1 - k) * 0.7 * pz.y]}
                >
                  <mesh geometry={caja}>
                    <Clay color={pz.color} />
                  </mesh>
                  {caras ? (
                    <mesh position={[0, 0, 0.165]}>
                      <planeGeometry args={[0.86, 0.86]} />
                      <meshStandardMaterial map={caras[i]} roughness={0.7} />
                    </mesh>
                  ) : null}
                  {/* Pestañas: un poco más gruesas que la pieza, así al encajar asoma su círculo en la vecina */}
                  {pz.tabs.map((d) => (
                    <mesh
                      key={d}
                      position={d === "der" ? [0.6, 0, 0] : [0, -0.6, 0]}
                      rotation={[Math.PI / 2, 0, 0]}
                    >
                      <cylinderGeometry args={[0.16, 0.16, 0.335, 32]} />
                      <Clay color={pz.color} />
                    </mesh>
                  ))}
                </group>
              );
            })}
            {/* Anillo de luz al encajar */}
            {tras > 0 && tras < 0.9 ? (
              <mesh rotation={[0, 0, 0]} scale={1 + tras * 1.2}>
                <torusGeometry args={[1.25, 0.03, 12, 72]} />
                <meshStandardMaterial
                  color="#FFF3DF"
                  emissive={C.durazno}
                  emissiveIntensity={0.9}
                  transparent
                  opacity={1 - tras / 0.9}
                />
              </mesh>
            ) : null}
          </group>
        );
      }}
    </Escena>
  );
};

// ---------- 2 · Gota en la zona: cae, se extiende solo dentro del anillo y el equipo se desliza ----------
const gotaGeom = (r: number, h: number) => {
  const pts: THREE.Vector2[] = [];
  for (let i = 0; i <= 40; i++) {
    const a = (Math.PI * i) / 40;
    pts.push(
      new THREE.Vector2(
        r * Math.sin(a) * Math.pow((1 - Math.cos(a)) / 2, 0.55),
        (Math.cos(a) * h) / 2,
      ),
    );
  }
  return new THREE.LatheGeometry(pts.reverse(), 48);
};
export const GotaZona3D: React.FC<Props & { cae: number; desliza: number }> = ({
  cae,
  desliza,
  ...props
}) => {
  const base = useMemo(() => discoRedondeado(1.55, 0.2, 0.07), []);
  const gota = useMemo(() => gotaGeom(0.3, 0.8), []);
  const equipo = useMemo(() => discoRedondeado(0.42, 0.26, 0.1), []);
  const tAbs = useTAbs();
  return (
    <Escena {...props} z={9}>
      {(p, t) => {
        const dc = tAbs - cae;
        const k = CLAMP(dc / 0.42);
        const yGota = 2.4 - 2.25 * k * k;
        const extiende = suave((dc - 0.42) / 0.7);
        const anillo = suave((dc - 0.42 - 0.55) / 0.25);
        const ds = tAbs - desliza;
        const xEq = ds > 0 ? Math.sin(ds * 3.2) * 0.62 : 0;
        const eq = suave(ds / 0.3);
        return (
          <group scale={1.2 * (0.6 + 0.4 * p)} position={[0, -0.35, 0]} rotation={[0.62, Math.sin(t * 0.7) * 0.25, 0]}>
            <mesh geometry={base}>
              <Clay color={C.salvia} />
            </mesh>
            {/* Anillo de la zona: se enciende cuando el aceite llega al borde y no lo pasa */}
            <mesh position={[0, 0.115, 0]} rotation={[Math.PI / 2, 0, 0]}>
              <torusGeometry args={[1.22, 0.05 + 0.025 * anillo, 12, 72]} />
              <meshStandardMaterial
                color={C.durazno}
                emissive={C.durazno}
                emissiveIntensity={0.15 + 0.6 * anillo * (0.6 + 0.4 * Math.sin(t * 6))}
                roughness={0.5}
              />
            </mesh>
            {extiende > 0 ? (
              <mesh position={[0, 0.11, 0]} scale={[1.13 * extiende, 1, 1.13 * extiende]}>
                <cylinderGeometry args={[1, 1, 0.025, 64]} />
                <meshStandardMaterial color="#E4B373" roughness={0.12} metalness={0.08} />
              </mesh>
            ) : null}
            {dc > 0 && k < 1 ? (
              <mesh geometry={gota} position={[0, yGota, 0]}>
                <meshStandardMaterial color="#E9B66E" roughness={0.1} metalness={0.05} />
              </mesh>
            ) : null}
            {/* Salpicadura al tocar */}
            {dc > 0.42 && dc < 0.9 ? (
              <mesh position={[0, 0.13, 0]} rotation={[Math.PI / 2, 0, 0]} scale={0.3 + (dc - 0.42) * 2}>
                <torusGeometry args={[0.5, 0.03, 8, 48]} />
                <meshStandardMaterial color="#F3CFA0" transparent opacity={1 - (dc - 0.42) / 0.48} />
              </mesh>
            ) : null}
            {/* El equipo se desliza sobre el aceite ("conservar el deslizamiento"), con brillos detrás */}
            {eq > 0 ? (
              <group position={[xEq, 0.26, 0]} scale={eq}>
                <mesh geometry={equipo}>
                  <meshStandardMaterial color="#FBF8F3" roughness={0.35} />
                </mesh>
                <mesh position={[0, 0.14, 0]}>
                  <cylinderGeometry args={[0.24, 0.24, 0.03, 40]} />
                  <Clay color={C.petroleo} />
                </mesh>
                {[0.5, 0.75, 1.0].map((d, i) => (
                  <mesh
                    key={i}
                    position={[-Math.sign(Math.cos(ds * 3.2)) * d, -0.1, (i - 1) * 0.18]}
                    scale={[0.35 * Math.abs(Math.cos(ds * 3.2)), 1, 1]}
                  >
                    <boxGeometry args={[0.5, 0.012, 0.035]} />
                    <meshStandardMaterial color="#FFFFFF" emissive="#FFF3DF" emissiveIntensity={0.8} transparent opacity={0.8} />
                  </mesh>
                ))}
              </group>
            ) : null}
          </group>
        );
      }}
    </Escena>
  );
};

// ---------- 3 · Reloj de arena: se da la vuelta en "3 minutos" y la arena empieza a caer ----------
const perfilVidrio = () =>
  new THREE.LatheGeometry(
    new THREE.SplineCurve(
      [
        [0.001, -1.18],
        [0.58, -1.13],
        [0.66, -0.9],
        [0.6, -0.55],
        [0.3, -0.18],
        [0.075, 0],
        [0.3, 0.18],
        [0.6, 0.55],
        [0.66, 0.9],
        [0.58, 1.13],
        [0.001, 1.18],
      ].map(([r, y]) => new THREE.Vector2(r, y)),
    ).getPoints(80),
    48,
  );
export const RelojArena3D: React.FC<Props & { gira: number }> = ({ gira, ...props }) => {
  const vidrio = useMemo(perfilVidrio, []);
  const tapa = useMemo(() => discoRedondeado(0.86, 0.17, 0.06), []);
  const tAbs = useTAbs();
  return (
    <Escena {...props} z={9}>
      {(p, t) => {
        const dg = tAbs - gira;
        const giro = suave(dg / 0.55);
        const girando = dg > 0 && giro < 1;
        // Antes de girar: toda la arena abajo. Durante el giro, el montón gira con el reloj (queda arriba, punta
        // abajo). Después: arriba se vacía y abajo se llena.
        const k = girando || dg <= 0 ? 0 : CLAMP((dg - 0.55) / 4.5);
        const abajo = girando || dg <= 0 ? 1 : k;
        const arriba = girando || dg <= 0 ? 0 : 1 - k;
        return (
          <group scale={1.45 * (0.6 + 0.4 * p)} rotation={[0.12, Math.sin(t * 0.8) * 0.3, girando ? giro * Math.PI : 0]}>
            <mesh geometry={vidrio}>
              <meshStandardMaterial color="#DCEAE4" roughness={0.08} metalness={0.1} transparent opacity={0.38} />
            </mesh>
            {[-1.28, 1.28].map((y) => (
              <mesh key={y} geometry={tapa} position={[0, y, 0]}>
                <Clay color={C.petroleo} />
              </mesh>
            ))}
            {[0, 1, 2].map((i) => (
              <mesh key={i} position={[Math.sin((i * 2 * Math.PI) / 3) * 0.74, 0, Math.cos((i * 2 * Math.PI) / 3) * 0.74]}>
                <cylinderGeometry args={[0.055, 0.055, 2.5, 16]} />
                <Clay color={C.durazno} />
              </mesh>
            ))}
            {/* Arena de abajo: montón (cono hacia arriba) */}
            {abajo > 0.02 ? (
              <mesh position={[0, -1.12 + 0.3 * abajo, 0]}>
                <coneGeometry args={[0.55 * Math.sqrt(abajo), 0.6 * abajo, 40]} />
                <meshStandardMaterial color="#E4B373" roughness={0.9} />
              </mesh>
            ) : null}
            {/* Arena de arriba: cono con la punta abajo */}
            {arriba > 0.02 ? (
              <mesh position={[0, 0.1 + 0.3 * arriba + 0.08, 0]} rotation={[Math.PI, 0, 0]}>
                <coneGeometry args={[0.55 * Math.sqrt(arriba), 0.6 * arriba, 40]} />
                <meshStandardMaterial color="#E4B373" roughness={0.9} />
              </mesh>
            ) : null}
            {/* Hilo de arena */}
            {k > 0 && k < 1 ? (
              <mesh position={[0, -0.55 + 0.15 * abajo, 0]}>
                <cylinderGeometry args={[0.02, 0.02, 1.1 - 0.3 * abajo, 8]} />
                <meshStandardMaterial color="#E4B373" roughness={0.9} />
              </mesh>
            ) : null}
          </group>
        );
      }}
    </Escena>
  );
};

// ---------- 4 · Chevrones: "líneas ascendentes desde la parte baja hacia arriba" → se encienden de abajo arriba ----------
export const Chevrones3D: React.FC<Props> = (props) => {
  const barra = useMemo(() => new RoundedBoxGeometry(1.05, 0.3, 0.3, 4, 0.12), []);
  return (
    <Escena {...props} z={9}>
      {(p, t) => (
        <group scale={1.35 * (0.6 + 0.4 * p)} rotation={[0.2, -0.4 + Math.sin(t * 1.1) * 0.25, 0]} position={[0, Math.sin(t * 2) * 0.05, 0]}>
          {[0, 1, 2].map((i) => {
            const luz = Math.max(0, Math.sin(t * 5 - i * 1.1)) ** 2;
            const color = new THREE.Color(C.salvia).lerp(new THREE.Color(C.durazno), luz);
            return (
              <group key={i} position={[0, -0.95 + i * 0.95, 0]}>
                {[-1, 1].map((lado) => (
                  <mesh key={lado} geometry={barra} position={[lado * 0.36, -0.18, 0]} rotation={[0, 0, lado * -0.62]}>
                    <meshStandardMaterial color={color} emissive={C.durazno} emissiveIntensity={0.45 * luz} roughness={0.6} />
                  </mesh>
                ))}
              </group>
            );
          })}
        </group>
      )}
    </Escena>
  );
};

// ---------- 5 · Maniquí de torso: abdomen y laterales se encienden; ombligo prohibido; círculos; arrastre ----------
const PERFIL_TORSO = new THREE.SplineCurve(
  [
    [0.001, -1.02],
    [0.62, -1.0],
    [0.84, -0.72],
    [0.82, -0.45],
    [0.66, -0.05],
    [0.62, 0.15],
    [0.7, 0.45],
    [0.83, 0.78],
    [0.84, 1.02],
    [0.6, 1.25],
    [0.27, 1.38],
    [0.25, 1.55],
    [0.001, 1.58],
  ].map(([r, y]) => new THREE.Vector2(r, y)),
).getPoints(90);
const radioTorso = (y: number) => {
  for (let i = 1; i < PERFIL_TORSO.length; i++) {
    const a = PERFIL_TORSO[i - 1];
    const b = PERFIL_TORSO[i];
    if ((y - a.y) * (y - b.y) <= 0) return a.x + ((b.x - a.x) * (y - a.y)) / (b.y - a.y || 1);
  }
  return 0.6;
};
const SX = 1.1;
const SZ = 0.72;
const tramoTorso = (y0: number, y1: number, phi0: number, phiL: number) => {
  const pts = PERFIL_TORSO.filter((v) => v.y >= y0 && v.y <= y1).map((v) => new THREE.Vector2(v.x * 1.015, v.y));
  return new THREE.LatheGeometry(pts, 32, phi0, phiL);
};
/** Punto sobre la superficie del maniquí (ángulo phi: 0 = delante, π/2 = costado derecho de la imagen). */
const sobreTorso = (phi: number, y: number, fuera = 0.04): [number, number, number] => {
  const r = radioTorso(y) + fuera;
  return [Math.sin(phi) * r * SX, y, Math.cos(phi) * r * SZ];
};
export const Torso3D: React.FC<
  Props & { abdomen: number; laterales: number; ombligo: number; circulos: number; arrastre: number; hasta: number }
> = ({ abdomen, laterales, ombligo, circulos, arrastre, hasta, ...props }) => {
  const cuerpo = useMemo(() => new THREE.LatheGeometry(PERFIL_TORSO, 64), []);
  const frente = useMemo(() => tramoTorso(-0.78, 0.42, -0.8, 1.6), []);
  const latDer = useMemo(() => tramoTorso(-0.7, 0.42, 0.85, 0.95), []);
  const latIzq = useMemo(() => tramoTorso(-0.7, 0.42, -1.8, 0.95), []);
  const tAbs = useTAbs();
  const yOmb = -0.2;
  return (
    <Escena {...props} z={10}>
      {(p, t) => {
        const la = suave((tAbs - abdomen) / 0.4);
        const ll = suave((tAbs - laterales) / 0.4);
        const lo = suave((tAbs - ombligo) / 0.35);
        const lc = tAbs >= circulos && tAbs < arrastre ? suave((tAbs - circulos) / 0.3) : 0;
        const lr = tAbs >= arrastre ? suave((tAbs - arrastre) / 0.4) * (1 - suave((tAbs - hasta + 0.3) / 0.3)) : 0;
        // Vista: gira hacia el costado en "laterales" y en el arrastre (desde la espalda)
        const giroLat = ll * (1 - suave((tAbs - laterales - 1.1) / 0.6)) * 0.75;
        const vista = Math.sin(t * 0.6) * 0.18 + giroLat + lr * 0.8;
        const brillo = (k: number) => ({
          color: new THREE.Color(C.salvia),
          emissive: new THREE.Color(C.salvia),
          emissiveIntensity: k * (0.22 + 0.1 * Math.sin(t * 5)),
          transparent: true,
          opacity: 0.88 * k,
          roughness: 0.6,
        });
        const orbita = [...Array(9)].map((_, i) => {
          const a = -(tAbs - circulos) * 4.2 + i * 0.16;
          const x = Math.cos(a) * 0.4;
          const y = yOmb + Math.sin(a) * 0.36;
          const phi = Math.asin(Math.max(-1, Math.min(1, x / (radioTorso(y) * SX))));
          return { pos: sobreTorso(phi, y, 0.06), s: 1 - i / 9 };
        });
        const estelas = [0, 1, 2, 3].map((i) => {
          const u = ((tAbs - arrastre) * 0.75 + i / 4) % 1;
          const lado = i % 2 ? 1 : -1;
          const phi = lado * (Math.PI * 0.92 - u * (Math.PI * 0.92 - 0.42));
          const y = 0.12 - u * 0.95;
          return { pos: sobreTorso(phi, y, 0.07), s: Math.sin(u * Math.PI) };
        });
        return (
          <group scale={1.15 * (0.6 + 0.4 * p)} position={[0, 0.15, 0]} rotation={[0.08, vista, 0]}>
            <group scale={[SX, 1, SZ]}>
              <mesh geometry={cuerpo}>
                <Clay color={MARFIL3D} rough={0.6} />
              </mesh>
              {la > 0.01 ? (
                <mesh geometry={frente}>
                  <meshStandardMaterial {...brillo(la)} />
                </mesh>
              ) : null}
              {ll > 0.01 ? (
                <>
                  <mesh geometry={latDer}>
                    <meshStandardMaterial {...brillo(ll)} />
                  </mesh>
                  <mesh geometry={latIzq}>
                    <meshStandardMaterial {...brillo(ll)} />
                  </mesh>
                </>
              ) : null}
            </group>
            {/* Ombligo */}
            <mesh position={sobreTorso(0, yOmb, -0.01)}>
              <sphereGeometry args={[0.045, 16, 12]} />
              <Clay color={C.petroleo} />
            </mesh>
            {/* "Evita pasar directamente sobre el ombligo": señal de prohibido */}
            {lo > 0.01 ? (
              <group position={sobreTorso(0, yOmb, 0.07)} scale={0.4 + 0.6 * lo} rotation={[0, 0, (1 - lo) * -1]}>
                <mesh>
                  <torusGeometry args={[0.2, 0.035, 12, 40]} />
                  <Clay color={C.petroleo} />
                </mesh>
                <mesh rotation={[0, 0, -Math.PI / 4]} scale={[1, Math.max(0.01, lo), 1]}>
                  <boxGeometry args={[0.06, 0.4, 0.03]} />
                  <Clay color={C.petroleo} />
                </mesh>
              </group>
            ) : null}
            {/* "Círculos amplios": una bola recorre un círculo alrededor del ombligo, sin pasar por él */}
            {lc > 0.01
              ? orbita.map((o, i) => (
                  <mesh key={i} position={o.pos} scale={lc * o.s}>
                    <sphereGeometry args={[i === 0 ? 0.075 : 0.05, 16, 12]} />
                    <meshStandardMaterial color="#FFF3DF" emissive={C.durazno} emissiveIntensity={0.8} transparent opacity={i === 0 ? 1 : 0.7 * o.s} />
                  </mesh>
                ))
              : null}
            {/* "Arrastre desde la espalda hacia la cintura, bajando por la ingle" */}
            {lr > 0.01
              ? estelas.map((e, i) => (
                  <mesh key={i} position={e.pos} scale={lr * e.s}>
                    <sphereGeometry args={[0.08, 16, 12]} />
                    <meshStandardMaterial color="#FFF3DF" emissive={C.durazno} emissiveIntensity={0.9} />
                  </mesh>
                ))
              : null}
            {/* Soporte de maniquí */}
            <mesh position={[0, 1.62, 0]}>
              <sphereGeometry args={[0.16, 24, 16]} />
              <Clay color={C.petroleo} />
            </mesh>
            <mesh position={[0, -1.4, 0]}>
              <cylinderGeometry args={[0.06, 0.06, 0.8, 16]} />
              <Clay color={C.petroleo} />
            </mesh>
            <mesh position={[0, -1.82, 0]}>
              <cylinderGeometry args={[0.55, 0.62, 0.1, 40]} />
              <Clay color={C.petroleo} />
            </mesh>
          </group>
        );
      }}
    </Escena>
  );
};

// ---------- 6 · Medidor de intensidad: la aguja se queda en la zona baja; en "dolorosa" se tacha la zona alta ----------
const arcoGeom = (a0: number, a1: number) => new THREE.TorusGeometry(1.25, 0.17, 16, 48, a1 - a0);
export const Medidor3D: React.FC<Props & { niveles: [number, number][]; tacha?: number }> = ({
  niveles,
  tacha,
  ...props
}) => {
  const bajo = useMemo(() => arcoGeom(0.62 * Math.PI, Math.PI), []);
  const medio = useMemo(() => arcoGeom(0.3 * Math.PI, 0.6 * Math.PI), []);
  const alto = useMemo(() => arcoGeom(0, 0.28 * Math.PI), []);
  const placa = useMemo(() => {
    const s = new THREE.Shape();
    s.absarc(0, 0, 1.62, 0, Math.PI, false);
    s.lineTo(1.62, 0);
    return new THREE.ExtrudeGeometry(s, { depth: 0.16, bevelEnabled: true, bevelSize: 0.06, bevelThickness: 0.06, bevelSegments: 4 });
  }, []);
  const tAbs = useTAbs();
  let v = niveles[0][1];
  for (let i = 1; i < niveles.length; i++) {
    const [t0, v0] = niveles[i - 1];
    const [t1, v1] = niveles[i];
    if (tAbs >= t1) v = v1;
    else if (tAbs > t0) v = v0 + (v1 - v0) * suave((tAbs - t0) / Math.min(0.7, t1 - t0));
  }
  const dt = tacha === undefined ? 0 : suave((tAbs - tacha) / 0.3);
  return (
    <Escena {...props} z={9}>
      {(p, t) => (
        <group scale={1.35 * (0.6 + 0.4 * p)} position={[0, -0.45, 0]} rotation={[0.18, Math.sin(t * 0.9) * 0.22, 0]}>
          <mesh geometry={placa} position={[0, 0, -0.3]}>
            <Clay color={MARFIL3D} />
          </mesh>
          <mesh geometry={bajo} rotation={[0, 0, 0.62 * Math.PI]}>
            <Clay color={C.salvia} />
          </mesh>
          <mesh geometry={medio} rotation={[0, 0, 0.3 * Math.PI]}>
            <Clay color={C.durazno} />
          </mesh>
          <mesh geometry={alto}>
            <Clay color={C.petroleo} />
          </mesh>
          {/* Aguja: 0 = izquierda (baja), 1 = derecha (alta) */}
          <group rotation={[0, 0, Math.PI * (1 - v) + Math.sin(t * 7) * 0.015]} position={[0, 0, 0.15]}>
            <mesh position={[0.52, 0, 0]}>
              <boxGeometry args={[1.05, 0.09, 0.08]} />
              <Clay color={C.petroleo} />
            </mesh>
          </group>
          <mesh position={[0, 0, 0.18]}>
            <sphereGeometry args={[0.17, 24, 16]} />
            <Clay color={C.durazno} />
          </mesh>
          {dt > 0 ? (
            <group position={[Math.cos(0.14 * Math.PI) * 1.25, Math.sin(0.14 * Math.PI) * 1.25, 0.25]} scale={0.3 + 0.7 * dt}>
              {[1, -1].map((s) => (
                <mesh key={s} rotation={[0, 0, (s * Math.PI) / 4]}>
                  <boxGeometry args={[0.1, 0.62, 0.08]} />
                  <meshStandardMaterial color={C.durazno} emissive={C.durazno} emissiveIntensity={0.3} />
                </mesh>
              ))}
            </group>
          ) : null}
        </group>
      )}
    </Escena>
  );
};

// ---------- 7 · Espiral: círculos que, en "barridos ascendentes", pasan a pasadas de abajo arriba ----------
export const Espiral3D: React.FC<Props & { barre: number }> = ({ barre, ...props }) => {
  const tAbs = useTAbs();
  const pos = (tt: number): [number, number, number] => {
    if (tt < barre) {
      const a = -tt * 5;
      return [Math.cos(a) * 0.85, Math.sin(a) * 0.85, 0];
    }
    const u = ((tt - barre) / 0.62) % 3;
    const col = Math.floor(u);
    const k = u - col;
    return [(col - 1) * 0.62, -1.05 + 2.1 * suave(k), 0];
  };
  return (
    <Escena {...props} z={9}>
      {(p, t) => {
        const b = suave((tAbs - barre) / 0.3);
        return (
          <group scale={1.35 * (0.6 + 0.4 * p)} rotation={[0.3, -0.35 + Math.sin(t * 0.8) * 0.2, 0]}>
            <mesh rotation={[Math.PI / 2, 0, 0]} position={[0, 0, -0.08]}>
              <cylinderGeometry args={[1.32, 1.32, 0.14, 64]} />
              <Clay color={C.salvia} />
            </mesh>
            <group position={[0, 0, 0.06]}>
              {/* Guía: círculo y, después, tres líneas hacia arriba */}
              <mesh scale={1 - b}>
                <torusGeometry args={[0.85, 0.02, 8, 64]} />
                <meshStandardMaterial color={C.durazno} transparent opacity={0.7} />
              </mesh>
              {[-1, 0, 1].map((c) => (
                <group key={c} position={[c * 0.62, 0, 0]} scale={[1, b, 1]}>
                  <mesh>
                    <boxGeometry args={[0.03, 2.1, 0.01]} />
                    <meshStandardMaterial color={C.durazno} transparent opacity={0.7} />
                  </mesh>
                  <mesh position={[0, 1.12, 0]}>
                    <coneGeometry args={[0.09, 0.18, 16]} />
                    <meshStandardMaterial color={C.durazno} />
                  </mesh>
                </group>
              ))}
              {[...Array(12)].map((_, i) => (
                <mesh key={i} position={pos(tAbs - i * 0.028)} scale={1 - i / 12}>
                  <sphereGeometry args={[i === 0 ? 0.13 : 0.1, 16, 12]} />
                  <meshStandardMaterial color="#FFF3DF" emissive={C.durazno} emissiveIntensity={0.85} transparent opacity={i === 0 ? 1 : 0.75 * (1 - i / 12)} />
                </mesh>
              ))}
            </group>
          </group>
        );
      }}
    </Escena>
  );
};

// ---------- 8 · Reloj de tarjetas: "30 segundos" → la tarjeta de los segundos cae de 00 a 30 ----------
const medioDigito = (texto: string, mitad: "arriba" | "abajo") =>
  textura(512, 320, (ctx) => {
    ctx.fillStyle = C.petroleo;
    ctx.fillRect(0, 0, 512, 320);
    ctx.fillStyle = COLORS.marfil;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.font = "700 470px 'Glacial Indifference'";
    ctx.fillText(texto, 256, mitad === "arriba" ? 330 : -10);
  });
export const TarjetasReloj3D: React.FC<Props & { gira: number }> = ({ gira, ...props }) => {
  const fuente = useFuente("700 80px 'Glacial Indifference'");
  const bloque = useMemo(() => new RoundedBoxGeometry(1.25, 1.6, 0.36, 4, 0.1), []);
  const tex = useMemo(
    () =>
      fuente
        ? {
            min: [medioDigito("00", "arriba"), medioDigito("00", "abajo")],
            viejo: [medioDigito("00", "arriba"), medioDigito("00", "abajo")],
            nuevo: [medioDigito("30", "arriba"), medioDigito("30", "abajo")],
          }
        : null,
    [fuente],
  );
  const tAbs = useTAbs();
  const W = 1.1;
  const H = 0.69;
  return (
    <Escena {...props} z={9}>
      {(p, t) => {
        const g = suave((tAbs - gira) / 0.45);
        const ang = -Math.PI * g;
        const mitad = (map: THREE.Texture, y: number, rotX = 0) => (
          <mesh position={[0, y, 0]} rotation={[rotX, 0, 0]}>
            <planeGeometry args={[W, H]} />
            <meshStandardMaterial map={map} roughness={0.6} side={THREE.FrontSide} />
          </mesh>
        );
        return (
          <group scale={1.55 * (0.6 + 0.4 * p)} rotation={[0.15, -0.3 + Math.sin(t * 0.9) * 0.2, 0]}>
            {[-0.72, 0.72].map((x, i) => (
              <group key={x} position={[x, 0, 0]}>
                <mesh geometry={bloque}>
                  <Clay color={C.petroleo} />
                </mesh>
                {tex ? (
                  <group position={[0, 0, 0.19]}>
                    {i === 0 ? (
                      <>
                        {mitad(tex.min[0], H / 2 + 0.01)}
                        {mitad(tex.min[1], -H / 2 - 0.01)}
                      </>
                    ) : (
                      <>
                        {/* Detrás de la tarjeta que cae: arriba el número nuevo, abajo el viejo hasta que lo tapa */}
                        {mitad(tex.nuevo[0], H / 2 + 0.01)}
                        {mitad(g > 0.5 ? tex.nuevo[1] : tex.viejo[1], -H / 2 - 0.01)}
                        <group position={[0, 0, 0.012]} rotation={[ang, 0, 0]}>
                          {g < 0.5 ? mitad(tex.viejo[0], H / 2 + 0.01) : mitad(tex.nuevo[1], H / 2 + 0.01, Math.PI)}
                        </group>
                      </>
                    )}
                    <mesh position={[0, 0, 0.02]}>
                      <boxGeometry args={[W, 0.025, 0.01]} />
                      <meshStandardMaterial color="#2E3C3D" />
                    </mesh>
                  </group>
                ) : null}
              </group>
            ))}
            {[0.22, -0.22].map((y) => (
              <mesh key={y} position={[0, y, 0.1]}>
                <sphereGeometry args={[0.07, 16, 12]} />
                <Clay color={C.durazno} />
              </mesh>
            ))}
          </group>
        );
      }}
    </Escena>
  );
};

// ---------- 9 · Medalla: "rutina completa de 15 minutos" → gira y se queda de frente con brillos ----------
export const Medalla3D: React.FC<Props & { llega: number }> = ({ llega, ...props }) => {
  const fuente = useFuente("700 80px 'Glacial Indifference'");
  const disco = useMemo(() => discoRedondeado(1.0, 0.2, 0.07), []);
  const cinta = useMemo(() => new RoundedBoxGeometry(0.5, 1.5, 0.05, 2, 0.02), []);
  const cara = useMemo(
    () =>
      fuente
        ? textura(512, 512, (ctx) => {
            ctx.fillStyle = COLORS.marfil;
            ctx.beginPath();
            ctx.arc(256, 256, 256, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = C.petroleo;
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";
            ctx.font = "700 250px 'Glacial Indifference'";
            ctx.fillText("15", 256, 230);
            ctx.fillStyle = C.salvia;
            ctx.font = "700 76px 'Glacial Indifference'";
            ctx.fillText("MIN", 256, 392);
          })
        : null,
    [fuente],
  );
  const tAbs = useTAbs();
  return (
    <Escena {...props} z={9}>
      {(p, t) => {
        const g = suave((tAbs - llega) / 0.9);
        return (
          <group scale={1.3 * (0.6 + 0.4 * p)} position={[0, -0.3, 0]}>
            {[-1, 1].map((s) => (
              <mesh key={s} geometry={cinta} position={[s * 0.32, 1.25, -0.1]} rotation={[0, 0, s * 0.32]}>
                <Clay color={s < 0 ? C.salvia : C.petroleo} />
              </mesh>
            ))}
            <group rotation={[0, (1 - g) * Math.PI * 3 + Math.sin(t * 1.4) * 0.15, 0]}>
              <mesh geometry={disco} rotation={[Math.PI / 2, 0, 0]}>
                <meshStandardMaterial color="#E4B373" roughness={0.3} metalness={0.25} />
              </mesh>
              {cara ? (
                <mesh position={[0, 0, 0.105]}>
                  <circleGeometry args={[0.78, 64]} />
                  <meshStandardMaterial map={cara} roughness={0.6} />
                </mesh>
              ) : null}
              <mesh position={[0, 0, 0.1]}>
                <torusGeometry args={[0.84, 0.04, 12, 64]} />
                <meshStandardMaterial color="#F3CFA0" roughness={0.3} metalness={0.2} />
              </mesh>
            </group>
            {[0, 1, 2, 3, 4, 5].map((i) => {
              const a = i * 1.05 + 0.3;
              const tw = Math.max(0, Math.sin(t * 4 + i * 1.7));
              return (
                <mesh key={i} position={[Math.cos(a) * 1.4, Math.sin(a) * 1.25, 0.3]} scale={g * tw}>
                  <octahedronGeometry args={[0.1, 0]} />
                  <meshStandardMaterial color="#FFFFFF" emissive={C.durazno} emissiveIntensity={1} />
                </mesh>
              );
            })}
          </group>
        );
      }}
    </Escena>
  );
};
