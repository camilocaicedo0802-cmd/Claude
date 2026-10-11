// Paleta muestreada de la referencia (ver estilo.md §7) + colores del brief.
export const C = {
  bg: '#F0F0F0',
  dot: '#E3E3E3',
  cardDark: '#35193F',
  cardHi: '#4D3157',
  card: '#472052',
  cardLight: '#714181',
  text: '#3E1D49',
  textSoft: '#816D85',
  arc: '#8E8C91',
  white: '#FFFFFF',
  black: '#161616',
  screen: '#1B1020',
};

export const W = 1080;
export const H = 1920;
export const FPS = 30;
export const DURATION = 900;

export const FONT = 'Inter';

export const cardGradient = `linear-gradient(135deg, ${C.cardHi} 0%, ${C.cardDark} 38%, ${C.card} 72%, ${C.cardLight} 118%)`;
export const cardShadow = '0 22px 55px rgba(20,8,26,0.28), 0 6px 12px rgba(20,8,26,0.18)';
export const softShadow = '0 14px 34px rgba(20,8,26,0.16), 0 3px 8px rgba(20,8,26,0.10)';
