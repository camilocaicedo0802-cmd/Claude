import { ThreeCanvas } from "@remotion/three";
import React, { useEffect, useMemo, useState } from "react";
import {
  continueRender,
  delayRender,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import * as THREE from "three";
import { COLORS } from "../brand";
import { pop } from "./util";

// Objetos 3D de marca modelados con three.js (acabado "clay" mate, paleta de Beleza).
// Todo se anima con useCurrentFrame (nunca useFrame) para que el render sea determinista.

const C = {
  durazno: "#F3CFA0", // durazno más saturado: con la luz de estudio el #FAEDCD se ve blanco
  marfil: COLORS.marfil,
  salvia: COLORS.salvia,
  salviaOscuro: "#5A7762",
  petroleo: COLORS.petroleo,
  cristal: "#1E2A2B",
};

const Clay: React.FC<{
  color: string;
  rough?: number;
  side?: THREE.Side;
  map?: THREE.Texture;
}> = ({ color, rough = 0.62, side, map }) => (
  <meshStandardMaterial
    color={color}
    roughness={rough}
    metalness={0}
    side={side}
    map={map}
  />
);

/** Disco de bordes redondeados (torno): radio r, alto h, radio del canto rr. Eje Y. */
const discoRedondeado = (r: number, h: number, rr: number) => {
  const pts: THREE.Vector2[] = [new THREE.Vector2(0, -h / 2)];
  const esquina = (cx: number, cy: number, a0: number, a1: number) => {
    for (let i = 0; i <= 8; i++) {
      const a = a0 + ((a1 - a0) * i) / 8;
      pts.push(new THREE.Vector2(cx + rr * Math.cos(a), cy + rr * Math.sin(a)));
    }
  };
  esquina(r - rr, -h / 2 + rr, -Math.PI / 2, 0);
  esquina(r - rr, h / 2 - rr, 0, Math.PI / 2);
  pts.push(new THREE.Vector2(0, h / 2));
  return new THREE.LatheGeometry(pts, 64);
};

const textura = (
  w: number,
  h: number,
  dibujar: (ctx: CanvasRenderingContext2D) => void,
) => {
  const cv = document.createElement("canvas");
  cv.width = w;
  cv.height = h;
  dibujar(cv.getContext("2d") as CanvasRenderingContext2D);
  const t = new THREE.CanvasTexture(cv);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 8;
  return t;
};

// ---------- Escena común: luz de estudio suave y entrada con muelle ----------
type Props = {
  desde: number;
  ancho: number;
  alto: number;
  style?: React.CSSProperties;
};

const Escena: React.FC<
  Props & { children: (p: number, t: number) => React.ReactNode; z?: number }
> = ({ desde, ancho, alto, style, children, z = 8 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = pop(frame, fps, desde, 11);
  const t = frame / fps - desde;
  if (t < 0) return null;
  return (
    <div
      style={{
        position: "absolute",
        width: ancho,
        height: alto,
        filter: "drop-shadow(0 18px 26px rgba(69,89,90,.4))",
        ...style,
      }}
    >
      <ThreeCanvas
        width={ancho}
        height={alto}
        camera={{ position: [0, 0, z], fov: 30 }}
        gl={{ alpha: true, antialias: true }}
      >
        <ambientLight intensity={0.45} />
        <hemisphereLight args={["#FFF8EE", "#45595A", 0.8]} />
        <directionalLight position={[-5, 6, 6]} intensity={2.6} />
        <directionalLight
          position={[6, 1, 2]}
          intensity={0.7}
          color="#FAEDCD"
        />
        {children(p, t)}
      </ThreeCanvas>
    </div>
  );
};
const CLAMP = (x: number) => Math.min(1, Math.max(0, x));
const suave = (x: number) => {
  const c = CLAMP(x);
  return c * c * (3 - 2 * c);
};

/** Carga una fuente antes de dibujar texto en una textura 3D (si no, saldría con la fuente por defecto). */
const useFuente = (css: string) => {
  const [handle] = useState(() => delayRender(`Fuente 3D ${css}`));
  const [lista, setLista] = useState(false);
  useEffect(() => {
    document.fonts
      .load(css)
      .then(() => setLista(true))
      .catch(() => setLista(true));
  }, [css]);
  useEffect(() => {
    if (lista) continueRender(handle);
  }, [lista, handle]);
  return lista;
};

// ---------- 1 · Lupa: "revisa muy bien tu piel" → la lupa recorre de lado a lado con un destello ----------
export const Lupa3D: React.FC<Props> = (props) => (
  <Escena {...props}>
    {(p, t) => (
      <group
        scale={0.55 + 0.45 * p}
        position={[
          Math.sin(t * 2.2) * 0.35,
          0.25 + Math.cos(t * 2.2) * 0.12,
          0,
        ]}
        rotation={[0.15, -0.35 + Math.sin(t * 1.2) * 0.25, 0.12]}
      >
        <mesh>
          <torusGeometry args={[1.0, 0.17, 24, 64]} />
          <Clay color={C.petroleo} />
        </mesh>
        <mesh rotation={[Math.PI / 2, 0, 0]}>
          <cylinderGeometry args={[0.95, 0.95, 0.06, 64]} />
          <meshStandardMaterial
            color="#DCEAE4"
            roughness={0.08}
            metalness={0.1}
            transparent
            opacity={0.45}
          />
        </mesh>
        {/* Destello que cruza el cristal */}
        <mesh
          position={[-0.9 + ((t * 0.9) % 1.6) * 1.2, 0, 0.06]}
          rotation={[0, 0, Math.PI / 4]}
        >
          <boxGeometry args={[0.12, 1.3, 0.01]} />
          <meshStandardMaterial
            color="#FFFFFF"
            emissive="#FFFFFF"
            emissiveIntensity={0.5}
            transparent
            opacity={0.55}
          />
        </mesh>
        <group position={[0.98, -0.98, 0]} rotation={[0, 0, Math.PI / 4]}>
          <mesh position={[0, -0.75, 0]}>
            <cylinderGeometry args={[0.17, 0.2, 1.3, 24]} />
            <Clay color={C.salvia} />
          </mesh>
          <mesh position={[0, -1.42, 0]}>
            <sphereGeometry args={[0.2, 24, 16]} />
            <Clay color={C.durazno} />
          </mesh>
          <mesh position={[0, -0.05, 0]}>
            <cylinderGeometry args={[0.22, 0.22, 0.2, 24]} />
            <Clay color={C.petroleo} />
          </mesh>
        </group>
      </group>
    )}
  </Escena>
);

// ---------- 2 · Aceite: "siempre debes usar el aceite" → el frasco se inclina y caen gotas ----------
const perfilFrasco = () => {
  const pts = [
    [0, -1.4],
    [0.62, -1.4],
    [0.76, -1.3],
    [0.78, -1.1],
    [0.78, 0.35],
    [0.7, 0.6],
    [0.45, 0.78],
    [0.3, 0.85],
    [0.3, 1.0],
    [0, 1.0],
  ].map(([x, y]) => new THREE.Vector2(x, y));
  return new THREE.LatheGeometry(new THREE.SplineCurve(pts).getPoints(60), 64);
};
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
export const Aceite3D: React.FC<Props & { vierte: number }> = ({
  vierte,
  ...props
}) => {
  const fuente = useFuente("700 80px 'Glacial Indifference'");
  const frasco = useMemo(perfilFrasco, []);
  const gota = useMemo(() => gotaGeom(0.22, 0.6), []);
  const etiqueta = useMemo(
    () =>
      fuente
        ? textura(1024, 256, (ctx) => {
            ctx.fillStyle = C.marfil;
            ctx.fillRect(0, 0, 1024, 256);
            ctx.fillStyle = C.petroleo;
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";
            ctx.font = "700 96px 'Glacial Indifference'";
            ctx.fillText("DRENA OIL", 256, 112);
            ctx.font = "400 40px 'Glacial Indifference'";
            ctx.fillText("BELEZA", 256, 190);
          })
        : null,
    [fuente],
  );
  return (
    <Escena {...props} z={9}>
      {(p, t) => {
        const d = t - (vierte - props.desde);
        const inclina = suave(d / 0.5) * 1.9; // se inclina hasta verter
        const theta = -inclina;
        const pico = new THREE.Vector3(
          -Math.sin(theta) * 1.05,
          Math.cos(theta) * 1.05,
          0,
        );
        return (
          <group
            scale={0.5 + 0.5 * p}
            position={[0.15, 0.35, 0]}
            rotation={[0.08, 0, 0]}
          >
            <group rotation={[0, Math.sin(t * 1.1) * 0.25, theta]}>
              <mesh geometry={frasco}>
                <meshStandardMaterial
                  color="#E4B373"
                  roughness={0.22}
                  metalness={0.05}
                />
              </mesh>
              {etiqueta ? (
                <mesh position={[0, -0.35, 0]} rotation={[0, -Math.PI / 2, 0]}>
                  <cylinderGeometry args={[0.8, 0.8, 0.8, 64, 1, true]} />
                  <meshStandardMaterial
                    map={etiqueta}
                    roughness={0.7}
                    side={THREE.DoubleSide}
                  />
                </mesh>
              ) : null}
              <mesh position={[0, 1.15, 0]}>
                <cylinderGeometry args={[0.36, 0.36, 0.42, 32]} />
                <Clay color={C.petroleo} />
              </mesh>
            </group>
            {/* Gotas que caen del pico mientras vierte */}
            {d > 0.45
              ? [0, 1, 2].map((i) => {
                  const k = ((((d - 0.45) * 1.4 + i / 3) % 1) + 1) % 1;
                  return (
                    <mesh
                      key={i}
                      geometry={gota}
                      position={[
                        pico.x - 0.1,
                        pico.y - 0.25 - k * k * 2.4,
                        0.1,
                      ]}
                      scale={(1 - k * 0.3) * Math.min(1, k * 8)}
                    >
                      <meshStandardMaterial
                        color="#E9B66E"
                        roughness={0.12}
                        metalness={0.05}
                      />
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

// ---------- 3 · Agua prohibida: "no uses agua" → gota de agua y la señal de prohibido se cierra sobre ella ----------
export const SinAgua3D: React.FC<Props & { prohibe: number }> = ({
  prohibe,
  ...props
}) => {
  const gota = useMemo(() => gotaGeom(0.85, 2.2), []);
  return (
    <Escena {...props}>
      {(p, t) => {
        const s = suave((t - (prohibe - props.desde)) / 0.3);
        return (
          <group
            scale={0.55 + 0.45 * p}
            rotation={[0.1, Math.sin(t * 1.2) * 0.3, 0]}
          >
            <mesh
              geometry={gota}
              position={[0, -0.05 + Math.sin(t * 3) * 0.05, -0.1]}
              scale={[1, 1 - Math.sin(t * 6) * 0.03, 1]}
            >
              <meshStandardMaterial
                color="#BFDCE3"
                roughness={0.08}
                metalness={0.1}
                transparent
                opacity={0.92}
              />
            </mesh>
            <mesh position={[-0.25, 0.25, 0.6]}>
              <sphereGeometry args={[0.13, 16, 16]} />
              <meshStandardMaterial
                color="#FFFFFF"
                emissive="#FFFFFF"
                emissiveIntensity={0.5}
              />
            </mesh>
            <group scale={0.4 + 0.6 * s} rotation={[0, 0, (1 - s) * -1.2]}>
              <mesh>
                <torusGeometry args={[1.45, 0.16, 24, 72]} />
                <Clay color={C.petroleo} />
              </mesh>
              <mesh
                position={[0, 0, 0.45]}
                rotation={[0, 0, -Math.PI / 4]}
                scale={[1, Math.max(0.01, s), 1]}
              >
                <boxGeometry args={[0.3, 2.9, 0.22]} />
                <Clay color={C.petroleo} />
              </mesh>
            </group>
          </group>
        );
      }}
    </Escena>
  );
};

// ---------- 4 · Perilla de intensidad: "desde la intensidad más baja… aumenta solo si…" → los niveles se encienden ----------
export const Perilla3D: React.FC<Props & { niveles: [number, number][] }> = ({
  niveles,
  ...props
}) => {
  const base = useMemo(() => discoRedondeado(1.45, 0.4, 0.14), []);
  const perilla = useMemo(() => discoRedondeado(0.8, 0.6, 0.16), []);
  const { fps } = useVideoConfig();
  const frame = useCurrentFrame();
  const tAbs = frame / fps;
  // Nivel actual (1…5) interpolado entre los momentos en que lo dice
  let nivel = niveles[0][1];
  for (let i = 1; i < niveles.length; i++) {
    const [t0, n0] = niveles[i - 1];
    const [t1, n1] = niveles[i];
    if (tAbs >= t1) nivel = n1;
    else if (tAbs > t0)
      nivel = n0 + (n1 - n0) * suave((tAbs - t0) / Math.min(0.8, t1 - t0));
  }
  if (tAbs >= niveles[niveles.length - 1][0])
    nivel = niveles[niveles.length - 1][1];
  const ang = (nv: number) => (210 - (nv - 1) * 60) * (Math.PI / 180);
  return (
    <Escena {...props}>
      {(p, t) => (
        <group
          scale={0.55 + 0.45 * p}
          rotation={[0.35, -0.35 + Math.sin(t * 1.1) * 0.15, 0]}
        >
          <mesh geometry={base} rotation={[Math.PI / 2, 0, 0]}>
            <Clay color={C.salvia} />
          </mesh>
          <mesh
            geometry={perilla}
            rotation={[Math.PI / 2, 0, 0]}
            position={[0, 0, 0.35]}
          >
            <Clay color={C.durazno} />
          </mesh>
          <group
            position={[0, 0, 0.66]}
            rotation={[0, 0, ang(nivel) - Math.PI / 2]}
          >
            <mesh position={[0, 0.45, 0]}>
              <boxGeometry args={[0.16, 0.5, 0.06]} />
              <Clay color={C.petroleo} />
            </mesh>
          </group>
          {[1, 2, 3, 4, 5].map((n) => {
            const a = ang(n);
            const on = nivel >= n - 0.5;
            return (
              <mesh
                key={n}
                position={[Math.cos(a) * 1.15, Math.sin(a) * 1.15, 0.24]}
                rotation={[0, 0, a - Math.PI / 2]}
              >
                <boxGeometry args={[0.16, 0.3, 0.1]} />
                <meshStandardMaterial
                  color={on ? "#FFE3B8" : C.petroleo}
                  emissive={on ? "#F3CFA0" : "#000000"}
                  emissiveIntensity={on ? 0.6 : 0}
                  roughness={0.5}
                />
              </mesh>
            );
          })}
        </group>
      )}
    </Escena>
  );
};

// ---------- Flechas de movimiento: pasadas ascendentes (arriba) o descendentes (abajo) y círculos ----------
export const Flecha3D: React.FC<
  Props & { dir?: "arriba" | "abajo" | "der" | "izq" }
> = ({ dir = "arriba", ...props }) => (
  <Escena {...props}>
    {(p, t) => {
      const k = (t * 0.9) % 1;
      return (
        <group
          scale={1.35 * (0.55 + 0.45 * p)}
          rotation={[
            0.2,
            Math.sin(t * 1.3) * 0.4,
            { arriba: Math.PI, abajo: 0, der: Math.PI / 2, izq: -Math.PI / 2 }[
              dir
            ],
          ]}
        >
          {[0, 1].map((i) => {
            const kk = (k + i * 0.5) % 1;
            return (
              <group
                key={i}
                position={[0, 1.0 - kk * 2.0, 0]}
                scale={Math.sin(kk * Math.PI)}
              >
                <mesh position={[0, 0.35, 0]}>
                  <cylinderGeometry args={[0.2, 0.2, 0.9, 24]} />
                  <Clay color={i ? C.salvia : C.durazno} />
                </mesh>
                <mesh position={[0, -0.4, 0]} rotation={[Math.PI, 0, 0]}>
                  <coneGeometry args={[0.5, 0.65, 32]} />
                  <Clay color={i ? C.salvia : C.durazno} />
                </mesh>
              </group>
            );
          })}
        </group>
      );
    }}
  </Escena>
);
export const FlechaCirculo3D: React.FC<Props> = (props) => (
  <Escena {...props}>
    {(p, t) => {
      const arco = Math.PI * 1.55;
      return (
        <group scale={1.2 * (0.55 + 0.45 * p)} rotation={[0.45, -0.3, -t * 2.4]}>
          <mesh>
            <torusGeometry args={[1.0, 0.2, 24, 72, arco]} />
            <Clay color={C.salvia} />
          </mesh>
          <mesh
            position={[Math.cos(arco), Math.sin(arco), 0]}
            rotation={[0, 0, arco]}
          >
            <coneGeometry args={[0.42, 0.6, 32]} />
            <Clay color={C.durazno} />
          </mesh>
        </group>
      );
    }}
  </Escena>
);

// ---------- 6 · Botón de encendido: "apagar y limpiar muy bien tu dispositivo" → el botón se hunde y aparecen brillos ----------
export const Apagar3D: React.FC<Props & { apaga: number; limpia: number }> = ({
  apaga,
  limpia,
  ...props
}) => {
  const base = useMemo(() => discoRedondeado(1.35, 0.35, 0.12), []);
  const boton = useMemo(() => discoRedondeado(1.0, 0.5, 0.2), []);
  return (
    <Escena {...props}>
      {(p, t) => {
        const da = t - (apaga - props.desde);
        const pulsa = da > 0 ? Math.sin(CLAMP(da / 0.35) * Math.PI) : 0;
        const encendido = da < 0.15;
        const dl = t - (limpia - props.desde);
        return (
          <group
            scale={0.55 + 0.45 * p}
            rotation={[0.35, -0.3 + Math.sin(t * 1.1) * 0.15, 0]}
          >
            <mesh geometry={base} rotation={[Math.PI / 2, 0, 0]}>
              <Clay color={C.petroleo} />
            </mesh>
            <group position={[0, 0, 0.32 - pulsa * 0.18]}>
              <mesh geometry={boton} rotation={[Math.PI / 2, 0, 0]}>
                <Clay color={C.durazno} />
              </mesh>
              <group position={[0, -0.05, 0.27]}>
                <mesh rotation={[0, 0, Math.PI / 2 + 0.6]}>
                  <torusGeometry
                    args={[0.45, 0.08, 16, 48, Math.PI * 2 - 1.2]}
                  />
                  <meshStandardMaterial
                    color={encendido ? C.salvia : C.petroleo}
                    emissive={encendido ? C.salvia : "#000000"}
                    emissiveIntensity={encendido ? 0.5 : 0}
                  />
                </mesh>
                <mesh position={[0, 0.33, 0]}>
                  <boxGeometry args={[0.16, 0.5, 0.1]} />
                  <meshStandardMaterial
                    color={encendido ? C.salvia : C.petroleo}
                    emissive={encendido ? C.salvia : "#000000"}
                    emissiveIntensity={encendido ? 0.5 : 0}
                  />
                </mesh>
              </group>
            </group>
            {/* Brillos de "limpio" */}
            {dl > 0
              ? [
                  [-1.3, 1.1, 0.5, 0],
                  [1.35, 0.7, 0.4, 0.15],
                  [0.9, -1.25, 0.6, 0.3],
                ].map(([x, y, s0, d0], i) => {
                  const k = CLAMP((dl - d0) / 0.35);
                  return (
                    <mesh
                      key={i}
                      position={[x, y, 0.6]}
                      rotation={[0, 0, t * 2 + i]}
                      scale={[s0 * k * 0.5, s0 * k * 1.3, s0 * k * 0.5]}
                    >
                      <octahedronGeometry args={[0.6, 0]} />
                      <meshStandardMaterial
                        color="#FFFFFF"
                        emissive={C.durazno}
                        emissiveIntensity={0.8}
                      />
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

// ---------- Cronómetro: "durante 2 / 3 / 4 minutos" → la aguja da la vuelta mientras dura el tramo ----------
export const Cronometro3D: React.FC<Props & { hasta: number }> = ({
  hasta,
  ...props
}) => {
  const caja = useMemo(() => discoRedondeado(1.25, 0.5, 0.2), []);
  const esfera = useMemo(() => discoRedondeado(1.02, 0.56, 0.08), []);
  return (
    <Escena {...props}>
      {(p, t) => {
        const vuelta = CLAMP(t / Math.max(0.5, hasta - props.desde));
        return (
          <group
            scale={0.55 + 0.45 * p}
            rotation={[0.25, -0.3 + Math.sin(t * 1.1) * 0.15, 0]}
            position={[0, -0.15, 0]}
          >
            <mesh geometry={caja} rotation={[Math.PI / 2, 0, 0]}>
              <Clay color={C.salvia} />
            </mesh>
            <mesh
              geometry={esfera}
              rotation={[Math.PI / 2, 0, 0]}
              position={[0, 0, 0.02]}
            >
              <Clay color={C.marfil} rough={0.7} />
            </mesh>
            {/* Corona y botón */}
            <mesh position={[0, 1.42, 0]}>
              <cylinderGeometry args={[0.18, 0.18, 0.3, 24]} />
              <Clay color={C.petroleo} />
            </mesh>
            <mesh position={[0, 1.62, 0]}>
              <cylinderGeometry args={[0.32, 0.32, 0.14, 32]} />
              <Clay color={C.durazno} />
            </mesh>
            {/* Arco que se llena con el tiempo */}
            <mesh
              position={[0, 0, 0.32]}
              rotation={[0, 0, Math.PI / 2]}
              scale={[-1, 1, 1]}
            >
              <torusGeometry
                args={[
                  0.82,
                  0.07,
                  12,
                  64,
                  Math.max(0.01, vuelta * Math.PI * 2),
                ]}
              />
              <meshStandardMaterial
                color={C.durazno}
                emissive={C.durazno}
                emissiveIntensity={0.35}
              />
            </mesh>
            {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11].map((i) => (
              <mesh
                key={i}
                position={[
                  Math.sin((i * Math.PI) / 6) * 0.68,
                  Math.cos((i * Math.PI) / 6) * 0.68,
                  0.31,
                ]}
                rotation={[0, 0, (-i * Math.PI) / 6]}
              >
                <boxGeometry args={[0.05, i % 3 === 0 ? 0.16 : 0.09, 0.03]} />
                <Clay color={C.petroleo} />
              </mesh>
            ))}
            <group
              position={[0, 0, 0.36]}
              rotation={[0, 0, -vuelta * Math.PI * 2]}
            >
              <mesh position={[0, 0.3, 0]}>
                <boxGeometry args={[0.07, 0.62, 0.04]} />
                <Clay color={C.petroleo} />
              </mesh>
            </group>
            <mesh position={[0, 0, 0.38]} rotation={[Math.PI / 2, 0, 0]}>
              <cylinderGeometry args={[0.08, 0.08, 0.06, 20]} />
              <Clay color={C.durazno} />
            </mesh>
          </group>
        );
      }}
    </Escena>
  );
};
