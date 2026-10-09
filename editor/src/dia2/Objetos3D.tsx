import { ThreeCanvas } from "@remotion/three";
import React, { useEffect, useMemo, useState } from "react";
import { continueRender, delayRender, useCurrentFrame, useVideoConfig } from "remotion";
import * as THREE from "three";
import { COLORS } from "../brand";
import { pop } from "./timing";

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

const Clay: React.FC<{ color: string; rough?: number; side?: THREE.Side; map?: THREE.Texture }> = ({ color, rough = 0.62, side, map }) => (
  <meshStandardMaterial color={color} roughness={rough} metalness={0} side={side} map={map} />
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

/** Rectángulo redondeado extruido con bisel (piezas "clay"). Centrado en el origen. */
const losa = (w: number, h: number, r: number, prof: number, bisel = 0.08, agujeros: THREE.Path[] = []) => {
  const s = new THREE.Shape();
  s.moveTo(-w / 2 + r, -h / 2);
  s.lineTo(w / 2 - r, -h / 2);
  s.absarc(w / 2 - r, -h / 2 + r, r, -Math.PI / 2, 0, false);
  s.lineTo(w / 2, h / 2 - r);
  s.absarc(w / 2 - r, h / 2 - r, r, 0, Math.PI / 2, false);
  s.lineTo(-w / 2 + r, h / 2);
  s.absarc(-w / 2 + r, h / 2 - r, r, Math.PI / 2, Math.PI, false);
  s.lineTo(-w / 2, -h / 2 + r);
  s.absarc(-w / 2 + r, -h / 2 + r, r, Math.PI, Math.PI * 1.5, false);
  s.holes.push(...agujeros);
  const g = new THREE.ExtrudeGeometry(s, { depth: prof, bevelEnabled: bisel > 0, bevelThickness: bisel, bevelSize: bisel, bevelSegments: 6, curveSegments: 24 });
  g.translate(0, 0, -prof / 2);
  return g;
};

const textura = (w: number, h: number, dibujar: (ctx: CanvasRenderingContext2D) => void) => {
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
type Props = { desde: number; ancho: number; alto: number; style?: React.CSSProperties };

const Escena: React.FC<Props & { children: (p: number, t: number) => React.ReactNode; z?: number }> = ({ desde, ancho, alto, style, children, z = 8 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = pop(frame, fps, desde, 11);
  const t = frame / fps - desde;
  if (t < 0) return null;
  return (
    <div style={{ position: "absolute", width: ancho, height: alto, filter: "drop-shadow(0 18px 26px rgba(69,89,90,.4))", ...style }}>
      <ThreeCanvas width={ancho} height={alto} camera={{ position: [0, 0, z], fov: 30 }} gl={{ alpha: true, antialias: true }}>
        <ambientLight intensity={0.45} />
        <hemisphereLight args={["#FFF8EE", "#45595A", 0.8]} />
        <directionalLight position={[-5, 6, 6]} intensity={2.6} />
        <directionalLight position={[6, 1, 2]} intensity={0.7} color="#FAEDCD" />
        {children(p, t)}
      </ThreeCanvas>
    </div>
  );
};

// ---------- 1 · Pin de ubicación: "fijar nuestro punto de partida" → el pin cae y se clava en su base ----------
export const Pin3D: React.FC<Props & { clavado: number }> = ({ clavado, ...props }) => {
  const cabeza = useMemo(() => {
    const T = new THREE.Vector2(0, -1.75);
    const cy = 0.35;
    const s = new THREE.Shape();
    const a = (61.6 * Math.PI) / 180;
    s.moveTo(T.x, T.y);
    s.lineTo(Math.cos(-Math.PI / 2 + a), cy + Math.sin(-Math.PI / 2 + a));
    s.absarc(0, cy, 1, -Math.PI / 2 + a, Math.PI * 1.5 - a, false);
    s.lineTo(T.x, T.y);
    const hueco = new THREE.Path();
    hueco.absarc(0, cy, 0.4, 0, Math.PI * 2, true);
    s.holes.push(hueco);
    const g = new THREE.ExtrudeGeometry(s, { depth: 0.45, bevelEnabled: true, bevelThickness: 0.2, bevelSize: 0.16, bevelSegments: 10, curveSegments: 64 });
    g.translate(0, 0, -0.225);
    return g;
  }, []);
  const base = useMemo(() => discoRedondeado(1.3, 0.42, 0.16), []);
  const bandera = useMemo(() => {
    const s = new THREE.Shape();
    s.moveTo(0, 0);
    s.lineTo(0.75, -0.05);
    s.lineTo(0.55, -0.25);
    s.lineTo(0.75, -0.45);
    s.lineTo(0, -0.5);
    const g = new THREE.ExtrudeGeometry(s, { depth: 0.04, bevelEnabled: true, bevelThickness: 0.03, bevelSize: 0.03, bevelSegments: 3 });
    return g;
  }, []);
  const { fps } = useVideoConfig();
  const frame = useCurrentFrame();
  return (
    <Escena {...props} z={9.5}>
      {(p, t) => {
        // Cae desde arriba y rebota al clavarse en la base
        const caida = pop(frame, fps, clavado - 0.25, 9);
        const yCabeza = 4.5 * (1 - caida);
        const aplasta = 1 - 0.12 * Math.max(0, Math.sin(Math.min(1, (t - (clavado - props.desde)) / 0.25) * Math.PI)) * (t > clavado - props.desde ? 1 : 0);
        const ondea = Math.sin(t * 6) * 0.12;
        return (
          <group scale={0.55 + 0.45 * p} rotation={[0.18, -0.7 + Math.sin(t * 1.1) * 0.3, 0]} position={[0, 0.2 + Math.sin(t * 2) * 0.05, 0]}>
            <mesh geometry={base} position={[0, -2.15, 0]} scale={[1, aplasta, 1]}>
              <Clay color={C.salvia} />
            </mesh>
            <mesh geometry={cabeza} position={[0, yCabeza + 0.05, 0]} scale={[1, 1, 1]}>
              <Clay color={C.durazno} rough={0.5} />
            </mesh>
            <group position={[0.95, -1.95, 0.35]}>
              <mesh position={[0, 0.7, 0]}>
                <cylinderGeometry args={[0.05, 0.05, 1.4, 16]} />
                <Clay color={C.petroleo} />
              </mesh>
              <mesh geometry={bandera} position={[0.03, 1.38, -0.02]} rotation={[0, ondea, 0]} scale={[Math.min(1, p * 1.2), 1, 1]}>
                <Clay color={C.petroleo} />
              </mesh>
            </group>
          </group>
        );
      }}
    </Escena>
  );
};

// ---------- 2 · Celular con cámara: "vas a tomar una foto" → el obturador se cierra y destella ----------
export const Camara3D: React.FC<Props & { disparo: number }> = ({ disparo, ...props }) => {
  const cuerpo = useMemo(() => losa(1.9, 3.1, 0.38, 0.28, 0.1), []);
  const pantalla = useMemo(() => losa(1.62, 2.82, 0.26, 0.02, 0.02), []);
  return (
    <Escena {...props}>
      {(p, t) => {
        const d = t - (disparo - props.desde);
        const cierre = d > 0 ? Math.sin(Math.min(1, d / 0.28) * Math.PI) : 0; // el diafragma se cierra y se abre
        const brillo = d > 0 ? Math.max(0, 1 - d / 0.35) : 0;
        return (
          <group scale={(0.55 + 0.45 * p) * (1 + 0.06 * cierre)} rotation={[0.1, 0.5 - p * 0.25 + Math.sin(t * 1.3) * 0.15, -0.12]}>
            <mesh geometry={cuerpo}>
              <Clay color={C.petroleo} />
            </mesh>
            <mesh geometry={pantalla} position={[0, 0, 0.26]}>
              <Clay color={C.durazno} rough={0.45} />
            </mesh>
            {/* Objetivo */}
            <group position={[0, 0.5, 0.32]}>
              <mesh rotation={[Math.PI / 2, 0, 0]}>
                <cylinderGeometry args={[0.55, 0.58, 0.18, 48]} />
                <Clay color={C.petroleo} />
              </mesh>
              <mesh position={[0, 0, 0.08]} scale={[1, 1, 0.55]}>
                <sphereGeometry args={[0.38, 48, 32]} />
                <meshStandardMaterial color={C.cristal} roughness={0.15} metalness={0.25} emissive="#FFFFFF" emissiveIntensity={brillo * 1.5} />
              </mesh>
              <mesh position={[-0.12, 0.13, 0.27]}>
                <sphereGeometry args={[0.07, 16, 16]} />
                <meshStandardMaterial color="#FFFFFF" emissive="#FFFFFF" emissiveIntensity={0.6} />
              </mesh>
            </group>
            {/* Diafragma: anillo salvia con hojas que se cierran en el disparo */}
            <group position={[0, -0.75, 0.3]}>
              <mesh>
                <torusGeometry args={[0.42, 0.09, 16, 48]} />
                <Clay color={C.salvia} />
              </mesh>
              {[0, 1, 2, 3, 4, 5].map((i) => (
                <mesh key={i} rotation={[0, 0, (i * Math.PI) / 3 + cierre * 0.5]} position={[0, 0, 0.01]}>
                  <boxGeometry args={[0.07, 0.36 + 0.12 * cierre, 0.05]} />
                  <Clay color={C.salvia} />
                </mesh>
              ))}
            </group>
            {[0.6, 0.15].map((y) => (
              <mesh key={y} position={[-1.02, y, 0]}>
                <boxGeometry args={[0.1, 0.32, 0.18]} />
                <Clay color={C.salvia} />
              </mesh>
            ))}
          </group>
        );
      }}
    </Escena>
  );
};

// ---------- 3 · Cinta métrica: "tomar tus medidas" → la cinta se desenrolla ----------
export const Cinta3D: React.FC<Props> = (props) => {
  const caja = useMemo(() => discoRedondeado(1.15, 0.75, 0.2), []);
  const tapa = useMemo(() => discoRedondeado(0.86, 0.8, 0.12), []);
  const marcas = useMemo(
    () =>
      textura(1024, 128, (ctx) => {
        ctx.fillStyle = C.durazno;
        ctx.fillRect(0, 0, 1024, 128);
        ctx.fillStyle = C.petroleo;
        for (let i = 0; i < 64; i++) {
          const x = 8 + i * 16;
          const largo = i % 5 === 0 ? 52 : 30;
          ctx.fillRect(x, 0, 4, largo);
        }
      }),
    [],
  );
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const curva = useMemo(
    () =>
      new THREE.CatmullRomCurve3([
        new THREE.Vector3(0, -1.12, 0),
        new THREE.Vector3(0.9, -1.2, 0),
        new THREE.Vector3(1.9, -1.05, 0),
        new THREE.Vector3(2.6, -0.55, 0),
        new THREE.Vector3(2.75, 0.05, 0),
      ]),
    [],
  );
  const desenrolla = Math.min(1, Math.max(0, pop(frame, fps, props.desde + 0.25, 16)));
  const cinta = useMemo(() => {
    const N = 60;
    const W = 0.62;
    const pos: number[] = [];
    const uv: number[] = [];
    const idx: number[] = [];
    const u1 = Math.max(0.02, desenrolla);
    for (let i = 0; i <= N; i++) {
      const u = (u1 * i) / N;
      const pt = curva.getPointAt(u);
      pos.push(pt.x, pt.y, pt.z - W / 2, pt.x, pt.y, pt.z + W / 2);
      uv.push(u * 1.6, 1, u * 1.6, 0);
      if (i < N) {
        const k = i * 2;
        idx.push(k, k + 1, k + 2, k + 1, k + 3, k + 2);
      }
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
    g.setAttribute("uv", new THREE.Float32BufferAttribute(uv, 2));
    g.setIndex(idx);
    g.computeVertexNormals();
    return { g, punta: curva.getPointAt(u1), tangente: curva.getTangentAt(u1) };
  }, [curva, desenrolla]);
  marcas.wrapS = THREE.RepeatWrapping;
  return (
    <Escena {...props}>
      {(p, t) => (
        <group scale={0.5 + 0.5 * p} position={[-0.9, 0.35, 0]} rotation={[0.55, -0.35 + Math.sin(t * 1.1) * 0.12, 0.05]}>
          <mesh geometry={caja} rotation={[Math.PI / 2, 0, 0]}>
            <Clay color={C.salvia} />
          </mesh>
          <mesh geometry={tapa} rotation={[Math.PI / 2, 0, 0]}>
            <Clay color={C.durazno} />
          </mesh>
          <mesh rotation={[Math.PI / 2, 0, 0]} position={[0, 0, 0.42]}>
            <cylinderGeometry args={[0.28, 0.28, 0.12, 32]} />
            <Clay color={C.petroleo} />
          </mesh>
          <mesh geometry={cinta.g}>
            <Clay color="#FFFFFF" map={marcas} side={THREE.DoubleSide} />
          </mesh>
          <mesh position={[cinta.punta.x, cinta.punta.y, 0]} rotation={[0, 0, Math.atan2(cinta.tangente.y, cinta.tangente.x)]}>
            <boxGeometry args={[0.1, 0.26, 0.7]} />
            <Clay color={C.petroleo} />
          </mesh>
        </group>
      )}
    </Escena>
  );
};

// ---------- 4 · Libreta: "anota muy bien esto" → el lápiz escribe y aparecen los checks ----------
export const Libreta3D: React.FC<Props> = (props) => {
  const tapa = useMemo(() => losa(1.75, 2.3, 0.18, 0.06, 0.04), []);
  const hoja = useMemo(() => losa(1.6, 2.12, 0.12, 0.1, 0.03), []);
  return (
    <Escena {...props}>
      {(p, t) => {
        const escribir = Math.max(0, t - 0.35);
        const linea = (i: number) => Math.min(1, Math.max(0, (escribir - i * 0.45) / 0.4));
        const actual = Math.min(3, Math.floor(escribir / 0.45));
        const yLinea = 0.55 - actual * 0.42;
        const avance = linea(actual);
        return (
          <group scale={0.55 + 0.45 * p} rotation={[-0.55, Math.sin(t * 1.0) * 0.15, 0.08]} position={[0, -0.1, 0]}>
            {[-1, 1].map((lado) => (
              <group key={lado} rotation={[0, lado * -0.16, 0]}>
                <mesh geometry={tapa} position={[lado * 0.9, 0, -0.08]}>
                  <Clay color={C.salvia} />
                </mesh>
                <mesh geometry={hoja} position={[lado * 0.84, 0, 0.02]}>
                  <Clay color={C.marfil} rough={0.8} />
                </mesh>
                {lado < 0
                  ? // Página izquierda: tres checks
                    [0, 1, 2].map((i) => (
                      <group key={i} position={[-1.3, 0.55 - i * 0.55, 0.19]}>
                        <mesh rotation={[Math.PI / 2, 0, 0]} scale={Math.min(1, linea(i) * 2)}>
                          <cylinderGeometry args={[0.13, 0.13, 0.05, 24]} />
                          <Clay color={C.salvia} />
                        </mesh>
                        <mesh position={[0.27 + 0.3 * linea(i), 0, 0]} scale={[Math.max(0.01, linea(i)), 1, 1]}>
                          <boxGeometry args={[0.6, 0.07, 0.03]} />
                          <Clay color="#E2A970" />
                        </mesh>
                      </group>
                    ))
                  : // Página derecha: renglones que se escriben
                    [0, 1, 2, 3].map((i) => (
                      <mesh key={i} position={[0.35 + 0.5 * linea(i), 0.55 - i * 0.42, 0.19]} scale={[Math.max(0.01, linea(i)), 1, 1]}>
                        <boxGeometry args={[1.0, 0.07, 0.03]} />
                        <Clay color="#E2A970" />
                      </mesh>
                    ))}
              </group>
            ))}
            {/* Lápiz: la punta sigue el renglón que se está escribiendo */}
            <group position={[0.4 + avance * 1.0, yLinea + 0.85 + Math.sin(t * 22) * 0.03, 0.75]} rotation={[0.35, 0, -0.75]}>
              <mesh>
                <cylinderGeometry args={[0.13, 0.13, 1.7, 6]} />
                <Clay color={C.salvia} />
              </mesh>
              <mesh position={[0, -1.0, 0]} rotation={[Math.PI, 0, 0]}>
                <coneGeometry args={[0.13, 0.32, 6]} />
                <Clay color="#F2D2A6" />
              </mesh>
              <mesh position={[0, -1.19, 0]} rotation={[Math.PI, 0, 0]}>
                <coneGeometry args={[0.045, 0.1, 12]} />
                <Clay color={C.petroleo} />
              </mesh>
              <mesh position={[0, 0.95, 0]}>
                <cylinderGeometry args={[0.13, 0.13, 0.22, 24]} />
                <Clay color={C.durazno} />
              </mesh>
            </group>
            <mesh position={[0, -1.25, 0.05]}>
              <boxGeometry args={[0.18, 0.45, 0.03]} />
              <Clay color={C.petroleo} />
            </mesh>
          </group>
        );
      }}
    </Escena>
  );
};

const fotoTextura = (fondo: string) =>
  textura(512, 400, (ctx) => {
    ctx.fillStyle = C.marfil;
    ctx.fillRect(0, 0, 512, 400);
    ctx.fillStyle = fondo;
    ctx.fillRect(28, 28, 456, 344);
    ctx.fillStyle = C.durazno;
    ctx.beginPath();
    ctx.arc(370, 120, 42, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = "#E9B97F";
    ctx.beginPath();
    ctx.moveTo(28, 372);
    ctx.lineTo(180, 180);
    ctx.lineTo(290, 300);
    ctx.lineTo(360, 230);
    ctx.lineTo(484, 372);
    ctx.fill();
  });

// ---------- 5 · Carpeta "Día 1" con candado: "estos cambios son personales" → las fotos entran y el candado se cierra ----------
export const Carpeta3D: React.FC<Props & { cierra: number }> = ({ cierra, ...props }) => {
  const [handle] = useState(() => delayRender("Fuente de la etiqueta 3D"));
  const [fuente, setFuente] = useState(false);
  useEffect(() => {
    document.fonts
      .load("700 90px 'Glacial Indifference'")
      .then(() => setFuente(true))
      .catch(() => setFuente(true));
  }, []);
  useEffect(() => {
    if (fuente) continueRender(handle);
  }, [fuente, handle]);

  const trasera = useMemo(() => {
    const s = new THREE.Shape();
    s.moveTo(-1.45, -1.0);
    s.lineTo(1.45, -1.0);
    s.lineTo(1.45, 0.95);
    s.lineTo(-0.2, 0.95);
    s.lineTo(-0.4, 1.2);
    s.lineTo(-1.45, 1.2);
    s.lineTo(-1.45, -1.0);
    const g = new THREE.ExtrudeGeometry(s, { depth: 0.08, bevelEnabled: true, bevelThickness: 0.06, bevelSize: 0.06, bevelSegments: 4 });
    g.translate(0, 0, -0.04);
    return g;
  }, []);
  const frontal = useMemo(() => losa(2.95, 1.6, 0.16, 0.08, 0.06), []);
  const etiqueta = useMemo(() => losa(1.15, 0.5, 0.12, 0.02, 0.02), []);
  const cuerpoCandado = useMemo(() => losa(0.7, 0.55, 0.12, 0.2, 0.06), []);
  const fotos = useMemo(() => [fotoTextura(C.petroleo), fotoTextura(C.salvia)], []);
  const texEtiqueta = useMemo(
    () =>
      fuente
        ? textura(460, 200, (ctx) => {
            ctx.fillStyle = C.durazno;
            ctx.fillRect(0, 0, 460, 200);
            ctx.fillStyle = C.petroleo;
            ctx.font = "700 108px 'Glacial Indifference'";
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";
            ctx.fillText("Día 1", 230, 108);
          })
        : null,
    [fuente],
  );
  return (
    <Escena {...props} z={7.2}>
      {(p, t) => {
        const d = t - (cierra - props.desde);
        const entra = Math.min(1, Math.max(0, d / 0.45));
        const baja = 1 - Math.pow(1 - entra, 3);
        const candado = Math.min(1, Math.max(0, (d - 0.45) / 0.15));
        return (
          <group scale={0.55 + 0.45 * p} rotation={[0.08, -0.35 + Math.sin(t * 1.0) * 0.15, 0]} position={[0, -0.15, 0]}>
            <mesh geometry={trasera} position={[0, 0, -0.25]}>
              <Clay color={C.salviaOscuro} />
            </mesh>
            {fotos.map((tex, i) => (
              <mesh key={i} position={[-0.35 + i * 0.6, 0.85 - baja * 0.45 - i * 0.1, -0.12 + i * 0.06]} rotation={[0, 0, (i ? -1 : 1) * 0.08]}>
                <boxGeometry args={[1.5, 1.17, 0.03]} />
                <Clay color="#FFFFFF" map={tex} />
              </mesh>
            ))}
            <mesh geometry={frontal} position={[0, -0.25, 0.08]} rotation={[-0.1, 0, 0]}>
              <Clay color={C.salvia} />
            </mesh>
            <mesh geometry={etiqueta} position={[-0.62, -0.05, 0.25]} rotation={[-0.1, 0, 0]}>
              <Clay color={C.durazno} />
            </mesh>
            {texEtiqueta ? (
              <mesh position={[-0.62, -0.05, 0.3]} rotation={[-0.1, 0, 0]}>
                <planeGeometry args={[1.05, 0.46]} />
                <meshStandardMaterial map={texEtiqueta} roughness={0.6} />
              </mesh>
            ) : null}
            {/* Candado: el arco baja y se cierra cuando las fotos ya están dentro */}
            <group position={[0.85, -0.5, 0.42]} rotation={[-0.1, 0, 0]}>
              <mesh position={[0, 0.42 + 0.18 * (1 - candado), 0]}>
                <torusGeometry args={[0.22, 0.07, 16, 32, Math.PI]} />
                <Clay color={C.petroleo} />
              </mesh>
              {[-0.22, 0.22].map((x) => (
                <mesh key={x} position={[x, 0.35 + 0.18 * (1 - candado) - (x > 0 ? 0.0 : 0), 0]}>
                  <cylinderGeometry args={[0.07, 0.07, 0.16, 16]} />
                  <Clay color={C.petroleo} />
                </mesh>
              ))}
              <mesh geometry={cuerpoCandado}>
                <Clay color={C.petroleo} />
              </mesh>
              <mesh position={[0, 0.04, 0.2]} rotation={[Math.PI / 2, 0, 0]}>
                <cylinderGeometry args={[0.07, 0.07, 0.05, 20]} />
                <Clay color={C.durazno} />
              </mesh>
              <mesh position={[0, -0.07, 0.2]}>
                <boxGeometry args={[0.05, 0.14, 0.05]} />
                <Clay color={C.durazno} />
              </mesh>
            </group>
          </group>
        );
      }}
    </Escena>
  );
};
