const integer = new Intl.NumberFormat("es-CO", { maximumFractionDigits: 0 });

export function formatNumber(value: number) {
  return integer.format(Math.round(value));
}

export function pad2(n: number) {
  return String(n).padStart(2, "0");
}
