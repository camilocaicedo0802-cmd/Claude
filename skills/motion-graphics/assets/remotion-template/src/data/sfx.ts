// Mapa de efectos de sonido: un SFX por cada evento que la referencia sonoriza (ver estilo.md §8).
// t = segundo global; file = nombre en public/sfx sin extensión; vol 0–1; note = qué lo justifica.
export type Sfx = { t: number; file: string; vol: number; note: string };

export const SFX: Sfx[] = [
  // { t: 0.0, file: "whoosh_long", vol: 0.7, note: "entrada del primer objeto" },
];
