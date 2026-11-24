// Eventos de sonido: SOLO SFX de la carpeta del cliente (public/sfx_sel, copiados de "SFX PACK 1/2").
import { BLOQUES, ESCENAS, LIGHT_LEAK, UI, DURACION_TOTAL_S } from "./plan";
import { PALABRAS, f, fin, inicio, limpio } from "./util";
import { rangoTecleada, tiemposTecleo } from "./componentes/Subtitulos";
import { BUSQUEDA, tecleoBusqueda } from "./componentes/Escenas";

export type Sfx = { at: number; src: string; vol: number; dur?: number }; // at en fotogramas (60 fps)
const ev: Sfx[] = [];
const add = (at: number, src: string, vol: number, dur?: number) => ev.push({ at: Math.max(0, Math.round(at)), src, vol, dur });

// Tecleo: teclas mecánicas alternadas (regla del cliente: los textos llevan typing)
const teclas = ["tecla_1", "tecla_2", "tecla_3", "tecla_4", "tecla_5"];
let k = 0;
const tecla = (at: number, vol = 0.42) => add(at, teclas[k++ % teclas.length], vol);
const teclear = (desde: number, hasta: number, max = 7) => {
  const n = Math.max(2, Math.min(max, Math.round((hasta - desde) / 3)));
  for (let i = 0; i < n; i++) tecla(desde + ((hasta - desde) * i) / Math.max(1, n - 1), 0.36);
};
const txt = (idx: number[]) => idx.map((i) => limpio(PALABRAS[i].text)).join(" ").toUpperCase();

// Whoosh de corte: VS_Short Whoosh tiene el pico a 0,54 s → se adelanta 32 f
const whoosh = (enFrame: number, n: 1 | 2 | 3 | 6, vol = 0.32) => add(enFrame - 32, `whoosh_${n}`, vol);
const swoosh = (enFrame: number, n: 4 | 6 | 7, vol = 0.3) => add(enFrame - 3, `swoosh_${n}`, vol);

// ---- Subtítulos destacados ----
for (const b of BLOQUES) {
  if (!b.destacado.length) continue;
  const t0 = f(inicio(b.destacado[0]));
  if (b.estilo === "linea") teclear(t0 - 8, t0 + 8, 5);
  if (b.estilo === "detras") {
    const n = txt(b.destacado).length;
    teclear(t0 - 22, t0 - 22 + n * 1.5 + 6, 6);
    if (b.impacto) add(t0 - 6, "deep_hit", 0.3);
  }
  if (b.estilo === "tecleada" || b.estilo === "broll") {
    const r = rangoTecleada(b);
    for (const l of tiemposTecleo(txt(b.destacado), r.desde, r.hasta)) tecla(l.t, 0.4);
    if (b.impacto) add(r.desde, "sub_hit", 0.16);
  }
  if (b.pildora?.length) {
    add(f(inicio(b.pildora[0])) - 8, "pop", 0.28);
    for (const i of b.pildora) tecla(f(inicio(i)) - 4, 0.3);
  }
  if (b.icono) add((b.estilo === "linea" ? t0 + 4 : b.estilo === "detras" ? t0 + 10 : f(fin(b.destacado[b.destacado.length - 1]))), "pop", 0.22);
}

// ---- Superposiciones UI (pop / clic / contador / riser) ----
add(f(UI.almuerzo.desde), "pop", 0.3);
add(f(inicio(16)) - 6, "click_4", 0.4);
add(f(inicio(19)) - 6, "click_4", 0.4);
add(f(UI.almuerzo.hasta) - 8, "swoosh_7", 0.18);
add(f(UI.graficaSube.desde), "pop", 0.28);
add(f(UI.graficaSube.desde) + 8 + 50 - 105, "riser", 0.4); // pico del riser (1,75 s) al terminar de dibujar la curva
add(f(inicio(58)) - 6, "click_3", 0.45);
add(f(UI.gomitas.desde), "pop", 0.3);
add(f(inicio(94)) - 4, "contador", 0.16, 0.25);
add(f(inicio(94)) - 4, "click_4", 0.4);
add(f(inicio(95)) - 2, "click_4", 0.4);
add(f(inicio(96)) - 6, "pop", 0.25);

// ---- Escenas: whoosh en cada corte con desenfoque, swoosh en cortes secos ----
for (const e of ESCENAS) {
  const a = f(e.desde), b = f(e.hasta);
  if (e.tipo === "broll") { if (e.desde !== 11.5) whoosh(a, e.desde === 23.38 ? 2 : 1, 0.3); else swoosh(a, 6, 0.32); }
  if (e.tipo === "montaje") { whoosh(a, 3, 0.3); const n = e.clips.length, cada = Math.ceil((b - a) / n); for (let i = 1; i < n; i++) swoosh(a + i * cada, i % 2 ? 7 : 4, 0.24); }
  if (e.tipo === "mg-investigar") { whoosh(a, 2, 0.32); const tb = tecleoBusqueda(e.desde); for (let i = 0; i < BUSQUEDA.length; i += 2) if (BUSQUEDA[i] !== " ") tecla(tb.base + tb.desde + i * tb.paso, 0.26); }
  if (e.tipo === "mg-reloj") { whoosh(a, 6, 0.3); add(a + 2, "vidrio", 0.16); add(a + 10, "reloj", 0.5); swoosh(f(inicio(61)) - 6, 7, 0.32); swoosh(f(inicio(64)) - 6, 6, 0.32); }
  if (e.tipo === "mg-grafica") { whoosh(a, 3, 0.3); add(f(inicio(84)) - 6, "pop", 0.25); add(f(inicio(87)) - 16, "woosh_5", 0.22); add(f(inicio(87)) - 6, "pop", 0.25); }
  if (e.tipo === "mg-cierre") { whoosh(a, 1, 0.34); add(a + 4, "sub_hit", 0.14); add(a + 26, "pop", 0.28); add(a + 30, "notif", 0.12); }
  // vuelta al plano hablando
  if (e.tipo !== "mg-cierre" && e.desde !== 10.1 && e.desde !== 11.5) swoosh(b, 4, 0.22);
}
// MG: palabras clave dentro de los motion graphics llevan tecleo
for (const i of [40, 41, 78, 84, 87]) teclear(f(inicio(i)) - 20, f(inicio(i)) - 2, 6);

// ---- Light leak en el giro del guion ----
add(f(LIGHT_LEAK) - 22, "film_burn", 0.55);

// ---- Punches de cámara en cortes de salto (golpe de aire muy suave) ----
for (const t of [0.8, 5.57, 9.37, 16.2, 30.5, 34.89]) swoosh(f(t), 6, 0.12);

export const SFX: Sfx[] = ev.filter((e) => e.vol > 0).sort((a, b) => a.at - b.at);

// Música: −16 dB bajo la voz y sube en el cierre (§9)
export const volumenMusica = (frame: number) => {
  const cierre = f(DURACION_TOTAL_S - 1.9);
  if (frame < cierre) return 0.13;
  return Math.min(0.3, 0.13 + ((frame - cierre) / 30) * 0.17) * (frame > f(DURACION_TOTAL_S) - 40 ? Math.max(0, (f(DURACION_TOTAL_S) - frame) / 40) : 1);
};
