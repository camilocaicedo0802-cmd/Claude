import {loadFont} from '@remotion/fonts';
import {staticFile} from 'remotion';

// Tipografías del referente Grow (estilo_referente_grow.md §2-3)
export const INTER = 'InterGrow'; // grotesca negrita tipo Helvetica Neue Bold
export const GOTHIC = 'LeagueGothicGrow'; // ultracondensada (títulos gigantes detrás de la persona)
export const ANTON = 'AntonGrow'; // condensada gruesa (láminas a pantalla completa)
loadFont({family: INTER, url: staticFile('fonts/Inter.ttf'), weight: '100 900', format: 'truetype'});
loadFont({family: GOTHIC, url: staticFile('fonts/LeagueGothic.ttf'), format: 'truetype'});
loadFont({family: ANTON, url: staticFile('fonts/Anton-Regular.ttf'), format: 'truetype'});

export const P = {
  purple: '#9601FD',
  purpleHi: '#B701FC',
  purpleLo: '#7600FC',
  lavender: '#C7A6FF',
  gray: '#4E4A4B',
  ui: '#343434',
};
