// Sonido v2 (UGC sencillo). SOLO SFX de la carpeta del cliente (public/sfx_sel, copiados de "SFX PACK 1/2").
import { BLOQUES, DURACION_TOTAL_S, ESCENAS, UI } from "./plan";
import { PALABRAS, f, inicio, limpio } from "./util";

export type Sfx = { at: number; src: string; vol: number; dur?: number }; // at en fotogramas (60 fps)
const ev: Sfx[] = [];
const add = (at: number, src: string, vol: number, dur?: number) => ev.push({ at: Math.max(0, Math.round(at)), src, vol, dur });

// Tecleo SOLO en los textos grandes e importantes (regla del cliente): las palabras gigantes detrás de la
// cabeza y los titulares de los motion graphics. Una tecla cada 2 letras, sincronizada con la aparición
// letra a letra (1,5 f por letra → 1 tecla cada 3 f). Los destacados en línea del subtítulo van sin tecleo.
const teclas = ["tecla_1", "tecla_2", "tecla_3", "tecla_4", "tecla_5"];
let k = 0;
const teclearLetras = (desde: number, texto: string) => {
  const n = Math.ceil(texto.replace(/ /g, "").length / 2);
  for (let i = 0; i < n; i++) add(desde + 2 + i * 3, teclas[k++ % teclas.length], 0.38);
};
for (const b of BLOQUES) {
  if (!b.destacado.length) continue;
  const t0 = f(inicio(b.destacado[0]));
  if (b.estilo === "detras") teclearLetras(t0 - 22, b.destacado.map((i) => limpio(PALABRAS[i].text)).join(""));
  if (b.icono && b.estilo !== "mg") add(t0 + 4, "pop", 0.18);
}
// Titulares de los motion graphics (mismo arranque que TitularMG en MG.tsx)
teclearLetras(f(inicio(78)) - 20, "GLUCOSA");
teclearLetras(f(inicio(84)) - 18, "ARRIBA");
teclearLetras(f(inicio(87)) - 18, "BAJE");
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
// Motion graphics: pops en flechas y dato del estudio
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
