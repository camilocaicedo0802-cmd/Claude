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

// Objetos 3D nuevos del día 7 "Piernas ligeras" (acabado clay mate, paleta Beleza). Todo se anima con el fotograma.

// ---------- Pluma: "piernas ligeras" → una pluma que cae balanceándose, como una hoja ----------
const plumaGeom = () => {
  const s = new THREE.Shape();
  // Contorno del ala con muescas (las barbas separadas) a ambos lados del raquis
  const L = 2.2;
  const ancho = (y: number) => 0.42 * Math.sin(Math.PI * Math.pow(y / L, 0.8));
  s.moveTo(0, 0);
  const n = 14;
  for (let i = 1; i <= n; i++) {
    const y = (L * i) / n;
    const w = ancho(y) * (i % 4 === 0 ? 0.72 : 1);
    s.lineTo(w, y - 0.04);
  }
  for (let i = n; i >= 1; i--) {
    const y = (L * i) / n;
    const w = ancho(y) * (i % 5 === 2 ? 0.7 : 1);
    s.lineTo(-w * 0.85, y - 0.1);
  }
  s.lineTo(0, 0);
  const g = new THREE.ExtrudeGeometry(s, {
    depth: 0.03,
    bevelEnabled: true,
    bevelThickness: 0.02,
    bevelSize: 0.02,
    bevelSegments: 2,
  });
  g.translate(0, -L / 2, 0);
  return g;
};
export const Pluma3D: React.FC<Props> = (props) => {
  const ala = useMemo(plumaGeom, []);
  return (
    <Escena {...props}>
      {(p, t) => (
        <group
          scale={1.25 * (0.62 + 0.38 * p)}
          position={[Math.sin(t * 1.4) * 0.45, Math.cos(t * 2.8) * 0.12, 0]}
          rotation={[
            0.3,
            Math.sin(t * 0.9) * 0.6,
            -0.5 + Math.sin(t * 1.4) * 0.35,
          ]}
        >
          <mesh geometry={ala}>
            <Clay color={C.marfil} rough={0.75} />
          </mesh>
          {/* Punta durazno y raquis */}
          <mesh position={[0, 0.85, 0.04]} scale={[0.75, 0.35, 1]}>
            <sphereGeometry args={[0.32, 24, 16]} />
            <Clay color={C.durazno} />
          </mesh>
          <mesh position={[0, -0.25, 0.03]}>
            <cylinderGeometry args={[0.035, 0.05, 2.5, 12]} />
            <Clay color={C.salvia} />
          </mesh>
        </group>
      )}
    </Escena>
  );
};

// ---------- Batería: "cansada" → queda una raya que parpadea; "no quieres abandonar el hábito" → se recarga ----------
export const Bateria3D: React.FC<Props & { carga: number }> = ({
  carga,
  ...props
}) => {
  const cuerpo = useMemo(
    () => new RoundedBoxGeometry(1.5, 2.6, 1.0, 6, 0.28),
    [],
  );
  const raya = useMemo(
    () => new RoundedBoxGeometry(1.05, 0.42, 0.3, 4, 0.12),
    [],
  );
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const tAbs = frame / fps;
  const nivel = 1 + 3 * suave((tAbs - carga) / 1.4); // 1 raya → 4 rayas
  return (
    <Escena {...props}>
      {(p, t) => (
        <group
          scale={1.3 * (0.55 + 0.45 * p)}
          rotation={[0.15, -0.45 + Math.sin(t * 1.1) * 0.2, 0.06]}
        >
          <mesh geometry={cuerpo}>
            <meshStandardMaterial
              color={C.marfil}
              roughness={0.35}
              transparent
              opacity={0.55}
            />
          </mesh>
          <mesh position={[0, 1.45, 0]}>
            <cylinderGeometry args={[0.28, 0.28, 0.3, 24]} />
            <Clay color={C.petroleo} />
          </mesh>
          {[0, 1, 2, 3].map((i) => {
            const on = nivel >= i + 0.5;
            const baja = nivel < 1.5;
            const parpadeo = baja ? 0.5 + 0.5 * Math.sin(t * 9) : 1;
            return (
              <mesh key={i} geometry={raya} position={[0, -0.88 + i * 0.58, 0]}>
                <meshStandardMaterial
                  color={on ? (baja ? "#E9A27A" : C.salvia) : "#CFC6BC"}
                  emissive={on ? (baja ? "#E9A27A" : C.salvia) : "#000000"}
                  emissiveIntensity={on ? 0.35 * parpadeo : 0}
                  roughness={0.55}
                />
              </mesh>
            );
          })}
          {/* Rayo de carga al recargar */}
          {tAbs > carga ? (
            <mesh
              position={[0.95, 0.2, 0.3]}
              rotation={[0, 0, -0.35]}
              scale={suave((tAbs - carga) / 0.4) * (1 + 0.08 * Math.sin(t * 6))}
            >
              <coneGeometry args={[0.22, 0.75, 3]} />
              <meshStandardMaterial
                color="#FFE3B8"
                emissive={C.durazno}
                emissiveIntensity={0.7}
              />
            </mesh>
          ) : null}
        </group>
      )}
    </Escena>
  );
};

// ---------- Almohada: "descansar… con las piernas apoyadas sobre una almohada" → se hunde suavemente ----------
const almohadaGeom = () => {
  const g = new THREE.BoxGeometry(2.4, 1.5, 0.6, 40, 28, 6);
  const pos = g.attributes.position;
  for (let i = 0; i < pos.count; i++) {
    const x = pos.getX(i) / 1.2;
    const y = pos.getY(i) / 0.75;
    const z = pos.getZ(i);
    const bulto =
      Math.pow(Math.max(0, 1 - x * x), 0.7) *
      Math.pow(Math.max(0, 1 - y * y), 0.7);
    pos.setZ(i, Math.sign(z) * (0.04 + 0.42 * bulto));
    // esquinas un poco hacia dentro, como una almohada rellena
    pos.setX(i, pos.getX(i) * (1 - 0.06 * y * y));
    pos.setY(i, pos.getY(i) * (1 - 0.06 * x * x));
  }
  g.computeVertexNormals();
  return g;
};
export const Almohada3D: React.FC<Props & { apoya: number }> = ({
  apoya,
  ...props
}) => {
  const almohada = useMemo(almohadaGeom, []);
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const hunde = suave((frame / fps - apoya) / 0.8);
  return (
    <Escena {...props}>
      {(p, t) => (
        <group
          scale={1.25 * (0.55 + 0.45 * p)}
          rotation={[0.85, 0, 0.12 + Math.sin(t * 0.8) * 0.06]}
          position={[0, -0.1, 0]}
        >
          <mesh geometry={almohada} scale={[1, 1, 1 - 0.18 * hunde]}>
            <Clay color={C.durazno} rough={0.8} />
          </mesh>
          {/* Ribete salvia */}
          <mesh rotation={[0, 0, 0]} scale={[1.18, 0.73, 1]}>
            <torusGeometry args={[1, 0.035, 8, 64]} />
            <Clay color={C.salvia} />
          </mesh>
          {/* Respiración: tres burbujas durazno que suben despacio */}
          {[0, 1, 2].map((i) => {
            const k = (t * 0.35 + i / 3) % 1;
            return (
              <mesh
                key={i}
                position={[0.7 - i * 0.5, 0.2 + k * 0.4, 0.55 + k * 1.4]}
                scale={Math.sin(k * Math.PI) * (0.1 + 0.04 * i)}
              >
                <sphereGeometry args={[1, 16, 12]} />
                <meshStandardMaterial
                  color="#FFF3DF"
                  emissive={C.durazno}
                  emissiveIntensity={0.4}
                  transparent
                  opacity={0.85}
                />
              </mesh>
            );
          })}
        </group>
      )}
    </Escena>
  );
};

// ---------- Sello "Día 7": "cumpliste con tus 15 minutos" → el sello cae, estampa y suelta brillos ----------
export const Sello3D: React.FC<Props & { estampa: number }> = ({
  estampa,
  ...props
}) => {
  const fuente = useFuente("700 80px 'Glacial Indifference'");
  const disco = useMemo(() => discoRedondeado(1.35, 0.32, 0.12), []);
  const cara = useMemo(
    () =>
      fuente
        ? textura(512, 512, (ctx) => {
            ctx.fillStyle = C.salvia;
            ctx.beginPath();
            ctx.arc(256, 256, 256, 0, Math.PI * 2);
            ctx.fill();
            ctx.strokeStyle = C.marfil;
            ctx.lineWidth = 10;
            ctx.beginPath();
            ctx.arc(256, 256, 222, 0, Math.PI * 2);
            ctx.stroke();
            ctx.fillStyle = C.marfil;
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";
            ctx.font = "700 64px 'Glacial Indifference'";
            ctx.fillText("DÍA 7", 256, 168);
            ctx.font = "700 44px 'Glacial Indifference'";
            ctx.fillText("CUMPLIDO", 256, 372);
            // check
            ctx.lineWidth = 30;
            ctx.lineCap = "round";
            ctx.lineJoin = "round";
            ctx.strokeStyle = C.durazno;
            ctx.beginPath();
            ctx.moveTo(176, 262);
            ctx.lineTo(236, 318);
            ctx.lineTo(340, 214);
            ctx.stroke();
          })
        : null,
    [fuente],
  );
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const d = frame / fps - estampa;
  // Cae desde arriba girando y, al tocar, se aplasta un instante (estampa)
  const caida = 1 - suave(d / 0.35);
  const golpe = d > 0.35 ? Math.sin(CLAMP((d - 0.35) / 0.25) * Math.PI) : 0;
  return (
    <Escena {...props}>
      {(p, t) => (
        <group
          position={[0, caida * 2.6, caida * 1.5]}
          rotation={[0.25 + caida * 1.2, Math.sin(t * 0.9) * 0.25, caida * 0.8]}
          scale={[1 + golpe * 0.12, 1 + golpe * 0.12, 1 - golpe * 0.3]}
        >
          <mesh geometry={disco} rotation={[Math.PI / 2, 0, 0]}>
            <Clay color={C.petroleo} />
          </mesh>
          {cara ? (
            <mesh position={[0, 0, 0.17]}>
              <circleGeometry args={[1.18, 64]} />
              <meshStandardMaterial map={cara} roughness={0.7} />
            </mesh>
          ) : null}
          {d > 0.4
            ? [0, 1, 2, 3, 4, 5].map((i) => {
                const a = (i / 6) * Math.PI * 2 + 0.3;
                const k = CLAMP((d - 0.4) / 0.6);
                const r = 1.5 + k * 0.6;
                return (
                  <mesh
                    key={i}
                    position={[Math.cos(a) * r, Math.sin(a) * r, 0.3]}
                    rotation={[0, 0, t * 2 + i]}
                    scale={Math.sin(k * Math.PI) * 0.22 + 0.001}
                  >
                    <octahedronGeometry args={[1, 0]} />
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
      )}
    </Escena>
  );
};
