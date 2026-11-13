import {loadFont} from '@remotion/fonts';
import {staticFile} from 'remotion';

// Tipografía de la referencia → Outfit (ver estilo.md §2-3), cargada desde public/fonts
export const OUTFIT = 'Outfit';
for (const weight of ['500', '600', '800', '900']) {
  loadFont({family: OUTFIT, url: staticFile(`fonts/Outfit-${weight}.ttf`), weight, format: 'truetype'});
}

// Paleta de la referencia (estilo.md §9)
export const C = {
  // Morados de la "W" del logo GROW (degradado vertical medido sobre el PNG)
  purple: '#9601FD',
  purpleTop: '#B701FC',
  purpleBottom: '#7600FC',
  purpleShadow: '#3D0080',
  purpleGrad: 'linear-gradient(180deg, #B701FC 0%, #9601FD 50%, #7600FC 100%)',
  purpleGlow: 'rgba(150,1,253,0.5)',
  white: '#FFFFFF',
  subWhite: '#FFF5F4',
  black: '#0B0B0B',
  grid: '#2A2A2A',
  grid2: '#3A3A3A',
  light: '#F2F2F2',
  chrome: 'linear-gradient(180deg, #FFFFFF 0%, #ECECEC 35%, #BDBDBD 58%, #F4F4F4 100%)',
};

export const FPS = 30;
export const W = 1080;
export const H = 1920;
