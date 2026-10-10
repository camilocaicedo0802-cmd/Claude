import React, { useMemo } from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import * as THREE from "three";
import { C, CLAMP, Escena, Props, suave } from "../rutinas/Objetos3D";

// Día 6 · "Piernas y apariencia de la celulitis": mapa del cuerpo en 3D (maniquí clay de cintura a pies).
// La zona que se trabaja se enciende en salvia y sobre ella se dibuja el movimiento que dice la voz:
// líneas que suben (barridos largos de abajo hacia arriba) o un círculo que gira (círculos amplios).
// Con "evita pasar sobre la rodilla o la ingle" aparecen dos cruces en esos puntos.

export type ZonaCuerpo = "ninguna" | "todo" | "musloD" | "musloI" | "gluteos";
export type Modo = "nada" | "barridos" | "circulos";
export type Paso = { t: number; zona: ZonaCuerpo; modo?: Modo };

const BASE = new THREE.Color("#E9D9C6"); // marfil cálido (con la luz de estudio el #F5F0EC se ve blanco)
const LUZ = new THREE.Color(C.salvia);

const torno = (pts: number[][], n = 48) =>
  new THREE.LatheGeometry(
    new THREE.SplineCurve(
      pts.map(([r, y]) => new THREE.Vector2(r, y)),
    ).getPoints(n),
    48,
  );
// Perfiles (radio, y) en coordenadas locales: el muslo baja desde la cadera, la pantorrilla desde la rodilla
const MUSLO = [
  [0, 0.05],
  [0.33, 0.04],
  [0.42, -0.15],
  [0.41, -0.5],
  [0.35, -0.9],
  [0.27, -1.25],
  [0.22, -1.42],
  [0.001, -1.45],
];
const PANTORRILLA = [
  [0, 0],
  [0.2, -0.02],
  [0.25, -0.35],
  [0.23, -0.6],
  [0.16, -1.0],
  [0.11, -1.35],
  [0.001, -1.4],
];
const radioMuslo = (y: number) => {
  for (let i = 1; i < MUSLO.length; i++) {
    const [r0, y0] = MUSLO[i - 1];
    const [r1, y1] = MUSLO[i];
    if (y <= y0 && y >= y1) return r0 + ((r1 - r0) * (y - y0)) / (y1 - y0);
  }
  return 0.2;
};

const CADERA_Y = 1.22;
const CADERA_X = 0.4;
const LARGO_MUSLO = 1.4;
const INCL = Math.atan((CADERA_X - 0.27) / LARGO_MUSLO);

// Ángulo de la vista según la zona (la pierna que se trabaja gira hacia cámara; los glúteos, de espaldas)
const vista = (z: ZonaCuerpo, t: number) =>
  z === "gluteos"
    ? Math.PI
    : z === "todo"
      ? 0.5 + t * 0.9 // gira para enseñar muslos y glúteos
      : z === "musloD"
        ? 0.45
        : z === "musloI"
          ? -0.45
          : Math.sin(t * 1.1) * 0.25;
const luces = (z: ZonaCuerpo) => ({
  musloD: z === "musloD" || z === "todo" ? 1 : 0,
  musloI: z === "musloI" || z === "todo" ? 1 : 0,
  gluteos: z === "gluteos" || z === "todo" ? 1 : 0,
});

const Piel: React.FC<{ luz: number; t: number }> = ({ luz, t }) => {
  const color = BASE.clone().lerp(LUZ, luz * 0.85);
  return (
    <meshStandardMaterial
      color={color}
      emissive={LUZ}
      emissiveIntensity={luz * (0.16 + 0.1 * Math.sin(t * 5))}
      roughness={0.6}
      metalness={0}
    />
  );
};

// Trazos de luz que suben por una superficie (barridos): x relativos, de yA a yB, delante de la superficie
const Barridos: React.FC<{
  t: number;
  fuerza: number;
  yA: number;
  yB: number;
  z: (y: number) => number;
  xs: number[];
}> = ({ t, fuerza, yA, yB, z, xs }) => (
  <>
    {xs.map((x, i) => {
      const k = (t * 0.75 + i * 0.37) % 1;
      const y = yA + (yB - yA) * k;
      return (
        <mesh
          key={i}
          position={[x, y, z(y)]}
          scale={fuerza * Math.sin(k * Math.PI)}
        >
          <capsuleGeometry args={[0.045, 0.3, 6, 12]} />
          <meshStandardMaterial
            color="#FFF3DF"
            emissive={C.durazno}
            emissiveIntensity={0.8}
          />
        </mesh>
      );
    })}
  </>
);
// Círculo amplio: anillo con una bola que lo recorre
const Circulo: React.FC<{ t: number; fuerza: number; r?: number }> = ({
  t,
  fuerza,
  r = 0.22,
}) => (
  <group scale={fuerza}>
    <mesh>
      <torusGeometry args={[r, 0.028, 12, 48]} />
      <meshStandardMaterial
        color="#FFF3DF"
        emissive={C.durazno}
        emissiveIntensity={0.6}
      />
    </mesh>
    <mesh position={[Math.cos(-t * 4.5) * r, Math.sin(-t * 4.5) * r, 0.02]}>
      <sphereGeometry args={[0.075, 16, 12]} />
      <meshStandardMaterial color={C.petroleo} roughness={0.5} />
    </mesh>
  </group>
);
// Cruz de "evita" (rodilla, ingle)
const Cruz: React.FC<{ s: number; pos: [number, number, number] }> = ({
  s,
  pos,
}) =>
  s <= 0.01 ? null : (
    <group position={pos} scale={s}>
      {[Math.PI / 4, -Math.PI / 4].map((a) => (
        <mesh key={a} rotation={[0, 0, a]}>
          <boxGeometry args={[0.07, 0.34, 0.05]} />
          <meshStandardMaterial color={C.petroleo} roughness={0.5} />
        </mesh>
      ))}
    </group>
  );

export const Piernas3D: React.FC<
  Props & { pasos: Paso[]; evita?: [number, number] }
> = ({ pasos, evita, ...props }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const tAbs = frame / fps;
  const muslo = useMemo(() => torno(MUSLO), []);
  const pantorrilla = useMemo(() => torno(PANTORRILLA), []);

  let i = 0;
  while (i + 1 < pasos.length && pasos[i + 1].t <= tAbs) i++;
  const actual = pasos[i];
  const previo = pasos[Math.max(0, i - 1)];
  const k = i === 0 ? 1 : suave((tAbs - actual.t) / 0.5);
  const la = luces(actual.zona);
  const lp = luces(previo.zona);
  const luz = {
    musloD: lp.musloD + (la.musloD - lp.musloD) * k,
    musloI: lp.musloI + (la.musloI - lp.musloI) * k,
    gluteos: lp.gluteos + (la.gluteos - lp.gluteos) * k,
  };
  // Giro por el camino más corto (la vista "todo" va girando y acumula vueltas)
  const g0 = vista(previo.zona, tAbs);
  const dg = vista(actual.zona, tAbs) - g0;
  const giro = g0 + Math.atan2(Math.sin(dg), Math.cos(dg)) * k;
  const modo = actual.modo ?? "nada";
  const fuerzaModo = suave((tAbs - actual.t - 0.3) / 0.4);
  const sEvita = evita
    ? CLAMP((tAbs - evita[0]) / 0.25) * (1 - CLAMP((tAbs - evita[1]) / 0.25))
    : 0;

  const pierna = (lado: -1 | 1, t: number) => {
    // lado −1 = pierna derecha de ella (a la izquierda de la imagen)
    const encendida = lado === -1 ? luz.musloD : luz.musloI;
    const activa =
      (lado === -1 && actual.zona === "musloD") ||
      (lado === 1 && actual.zona === "musloI");
    const rodX = lado * (CADERA_X - Math.sin(INCL) * LARGO_MUSLO);
    const rodY = CADERA_Y - Math.cos(INCL) * LARGO_MUSLO;
    const zM = (y: number) => radioMuslo(y) + 0.03;
    return (
      <group key={lado}>
        <group
          position={[lado * CADERA_X, CADERA_Y, 0]}
          rotation={[0, 0, -lado * INCL]}
        >
          <mesh geometry={muslo}>
            <Piel luz={encendida} t={t} />
          </mesh>
          {activa && modo === "barridos" ? (
            <Barridos
              t={t}
              fuerza={fuerzaModo}
              yA={-1.15}
              yB={-0.2}
              z={zM}
              xs={[-0.15, 0, 0.15]}
            />
          ) : null}
          {activa && modo === "circulos" ? (
            <group position={[0, -0.6, zM(-0.6) + 0.01]}>
              <Circulo t={t} fuerza={fuerzaModo} />
            </group>
          ) : null}
          {activa ? (
            <Cruz s={sEvita} pos={[lado * -0.12, -0.08, 0.47]} />
          ) : null}
        </group>
        <mesh position={[rodX, rodY, 0]}>
          <sphereGeometry args={[0.21, 32, 24]} />
          <Piel luz={0} t={t} />
        </mesh>
        {activa ? <Cruz s={sEvita} pos={[rodX, rodY, 0.3]} /> : null}
        <mesh geometry={pantorrilla} position={[rodX, rodY, 0]}>
          <Piel luz={0} t={t} />
        </mesh>
        <mesh
          position={[rodX + lado * 0.02, rodY - 1.45, 0.12]}
          rotation={[Math.PI / 2, 0, 0]}
          scale={[1.25, 1, 1]}
        >
          <capsuleGeometry args={[0.1, 0.28, 6, 16]} />
          <Piel luz={0} t={t} />
        </mesh>
      </group>
    );
  };

  return (
    <Escena {...props} z={7.5}>
      {(p, t) => (
        <group
          scale={0.92 * (0.55 + 0.45 * p)}
          position={[0, -0.12, 0]}
          rotation={[0.12, giro, 0]}
        >
          {/* Cintura y cadera */}
          <mesh position={[0, 1.72, 0]}>
            <cylinderGeometry args={[0.55, 0.72, 0.45, 48]} />
            <Piel luz={0} t={t} />
          </mesh>
          <mesh position={[0, 1.3, 0]} scale={[0.8, 0.52, 0.48]}>
            <sphereGeometry args={[1, 48, 32]} />
            <Piel luz={0} t={t} />
          </mesh>
          {/* Glúteos (detrás) */}
          {[-1, 1].map((lado) => (
            <group key={lado} position={[lado * 0.3, 1.0, -0.14]}>
              <mesh scale={[1, 0.95, 0.85]}>
                <sphereGeometry args={[0.43, 40, 28]} />
                <Piel luz={luz.gluteos} t={t} />
              </mesh>
              {actual.zona === "gluteos" && modo === "circulos" ? (
                <group position={[0, 0, -0.39]} rotation={[0, Math.PI, 0]}>
                  <Circulo t={t + lado} fuerza={fuerzaModo} r={0.2} />
                </group>
              ) : null}
              {actual.zona === "gluteos" && modo === "barridos" ? (
                <group rotation={[0, Math.PI, 0]}>
                  <Barridos
                    t={t + (lado > 0 ? 0.2 : 0)}
                    fuerza={fuerzaModo}
                    yA={-0.3}
                    yB={0.3}
                    z={() => 0.4}
                    xs={[-0.12, 0.12]}
                  />
                </group>
              ) : null}
            </group>
          ))}
          {pierna(-1, t)}
          {pierna(1, t)}
        </group>
      )}
    </Escena>
  );
};
