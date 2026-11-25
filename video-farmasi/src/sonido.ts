// Sonido v2 (UGC sencillo). SOLO SFX de la carpeta del cliente (public/sfx_sel, copiados de "SFX PACK 1/2").
import { BLOQUES, DURACION_TOTAL_S, ESCENAS, UI } from "./plan";
import { PALABRAS, f, inicio, limpio } from "./util";

export type Sfx = { at: number; src: string; vol: number; dur?: number }; // at en fotogramas (60 fps)
const ev: Sfx[] = [];
const add = (at: number, src: string, vol: number, dur?: number) => ev.push({ at: Math.max(0, Math.round(at)), src, vol, dur });

// Tecleo suave en los destacados (regla del cliente): ≤ 4 teclas por destacado, vol. 0,3
const teclas = ["tecla_1", "tecla_2", "tecla_3", "tecla_4", "tecla_5"];
let k = 0;
const teclear = (desde: number, n: number) => {
  for (let i = 0; i < n; i++) add(desde + i * 3, teclas[k++ % teclas.length], 0.3);
};
for (const b of BLOQUES) {
  if (!b.destacado.length || b.estilo === "mg") continue;
  const t0 = f(inicio(b.destacado[0]));
  const letras = b.destacado.map((i) => limpio(PALABRAS[i].text)).join("").length;
  const n = Math.min(4, Math.max(2, Math.round(letras / 3)));
  teclear(b.estilo === "detras" ? t0 - 20 : t0 - 8, n);
  if (b.icono) add(t0 + 4, "pop", 0.18);
}
// Cortes a b-roll / imagen: swoosh suave. Entrada a motion graphic: whoosh (pico a 0,54 s → −32 f).
// Vuelta al plano hablando: swoosh muy suave (solo si no empieza otra escena justo ahí).
for (const e of ESCENAS) {
  if (e.tipo === "mg-glucosa" || e.tipo === "mg-grafica") add(f(e.desde) - 32, "whoosh_2", 0.26);
  else add(f(e.desde) - 3, "swoosh_6", 0.2);
  if (!ESCENAS.some((o) => Math.abs(o.desde - e.hasta) < 0.01)) add(f(e.hasta) - 3, "swoosh_4", 0.14);
}
// Tarjeta de glucosa sobre el plano hablando: pop + clic en el chip "SUBE"
add(f(UI.graficaSube.desde), "pop", 0.22);
add(f(inicio(58)) - 6, "click_4", 0.3);
// Chip "Carbohidratos → Glucosa": pop + clic cuando aparece "Glucosa"
add(f(UI.carbohidratos.desde) + 6, "pop", 0.22);
add(f(UI.carbohidratos.desde) + 30, "click_3", 0.3);
// Tarjeta de tiempo: pop, contador mientras se llena la barra y pop del "2–3 h"
add(f(UI.tiempo.desde) + 2, "pop", 0.22);
add(f(UI.tiempo.desde) + 14, "contador", 0.12, 1.0);
add(f(UI.tiempo.hasta) - 44, "pop", 0.24);
// Motion graphics: tecleo en los titulares y pops en flechas y dato del estudio
for (const i of [78, 84, 87]) teclear(f(inicio(i)) - 20, 4);
add(f(25.4), "pop", 0.2); // chip C6H12O6
add(f(inicio(84)) - 6, "pop", 0.22); // flecha arriba
add(f(inicio(87)) - 14, "woosh_5", 0.18); // la curva cae
add(f(inicio(87)) - 6, "pop", 0.22); // flecha abajo
add(f(inicio(85)) + 4, "click_4", 0.26); // dato del estudio
export const SFX: Sfx[] = ev.sort((a, b) => a.at - b.at);

// Cierre: pop en la píldora final
add(f(UI.cierre.desde), "pop", 0.24);

// Música: constante bajo la voz; cuando ella termina de hablar sube un poco y se funde en el último segundo
export const volumenMusica = (frame: number) => {
  const finF = f(DURACION_TOTAL_S);
  const finVoz = f(36.1);
  const base = frame < finVoz ? 0.12 : Math.min(0.2, 0.12 + ((frame - finVoz) / 30) * 0.08);
  return base * Math.min(1, Math.max(0, (finF - frame) / 60));
};
