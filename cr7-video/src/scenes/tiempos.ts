// [inicio, duración] de cada escena en fotogramas (30 fps). Cada corte cae 1–5 fotogramas
// antes de la primera palabra de su frase para que la imagen "aterrice" con la voz.
export const E = {
  intro: [0, 45],
  isla: [45, 57],
  nino: [102, 21],
  sueno: [123, 23],
  posib: [146, 80],
  united: [226, 73],
  madrid: [299, 33],
  mundo: [332, 62],
  disciplina: [394, 33],
  sacrificio: [427, 39],
  imparable: [466, 75],
  records: [541, 54],
  titulos: [595, 62],
  historia: [657, 88],
  cristiano: [745, 71],
  legado: [816, 87],
  negro: [903, 3],
} as const satisfies Record<string, readonly [number, number]>;

export const DURACION_TOTAL = 906; // 30,2 s
