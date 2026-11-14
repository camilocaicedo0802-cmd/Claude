import {Video} from '@remotion/media';
import {AbsoluteFill, Img, Sequence, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {clamp, easeOut} from '../engine/helpers';
import {OUTFIT} from '../v1/theme';
import {Cinta, Garabato, INK, PURPLE, Papelito, Pieza, Rasgado, Sello, TiraPapel, jitter, stepped, torn} from './Collage';
import {MODOS, SPEECH, T, TITLES, TOTAL, modoAt, ws} from './data';
import {LastFrame, Live} from './Live';

const F = 30;
const OUTLINE = 'drop-shadow(7px 0 0 #F4F1EC) drop-shadow(-7px 0 0 #F4F1EC) drop-shadow(0 7px 0 #F4F1EC) drop-shadow(0 -7px 0 #F4F1EC) drop-shadow(0 22px 26px rgba(0,0,0,0.6))';

const BVid: React.FC<{src: string; from: number}> = ({src, from}) => (
  <Sequence from={Math.round(from * F)} layout="none">
    <Video src={staticFile(src)} muted objectFit="cover" style={{width: '100%', height: '100%'}} />
  </Sequence>
);

// ---------------------------------------------------------------- la persona según el modo
export const Persona: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / F;
  const m = modoAt(t);
  if (m.mode === 'end') return null;
  if (m.mode === 'full') {
    return (
      <AbsoluteFill>
        <Live from={0} to={SPEECH} audio />
      </AbsoluteFill>
    );
  }
  if (m.mode === 'recorte') {
    const jt = jitter(frame, 4, 0.5);
    return (
      <>
        <AbsoluteFill style={{filter: OUTLINE, rotate: `${-1.5 + jt.r}deg`, scale: '0.97'}}>
          <Live from={0} to={SPEECH} audio mask="c" />
        </AbsoluteFill>
        <TiraPapel />
      </>
    );
  }
  // foto rasgada con cinta
  const f = m.foto!;
  const l = stepped(frame - m.t * F, 2);
  const p = interpolate(l, [0, 6], [0, 1], {...clamp, easing: easeOut});
  const jt = jitter(frame, 7, 0.6);
  const w = 1080 * f.k + 28;
  const h = 1920 * f.k + 28;
  return (
    <div
      style={{
        position: 'absolute',
        left: f.cx - w / 2,
        top: f.cy - h / 2,
        width: w,
        height: h,
        rotate: `${f.rot + (1 - p) * 7 + jt.r}deg`,
        scale: String(interpolate(p, [0, 1], [1.2, 1])),
        translate: `${jt.x}px ${jt.y}px`,
        filter: 'drop-shadow(0 24px 30px rgba(0,0,0,0.6))',
      }}
    >
      <div style={{position: 'absolute', inset: 0, background: '#F4F1EC', clipPath: torn(w, h, 21, 8)}} />
      <div style={{position: 'absolute', left: 14, top: 14, width: w - 28, height: h - 28, overflow: 'hidden', clipPath: torn(w - 28, h - 28, 29, 3, 22)}}>
        <div style={{position: 'absolute', left: 0, top: 0, width: 1080, height: 1920, transformOrigin: '0 0', scale: String(f.k)}}>
          <Live from={0} to={SPEECH} audio />
        </div>
      </div>
      <Cinta x={w * 0.5 - 90} y={-22} rot={-4} seed={3} />
    </div>
  );
};

// ---------------------------------------------------------------- piezas de cada escena
const Texto: React.FC<{size: number; weight?: number; color?: string; children: React.ReactNode}> = ({size, weight = 800, color = INK, children}) => (
  <div style={{fontSize: size, fontWeight: weight, color, lineHeight: 1.05, letterSpacing: '-0.02em'}}>{children}</div>
);

export const Escenas: React.FC = () => (
  <>
    {/* S2 · no vendes en redes */}
    <Pieza at={ws(8)} until={T.c2} x={40} y={130} w={440} h={330} rot={-6} seed={2}>
      <Papelito w={440} h={330} seed={4}>
        <Texto size={30} weight={700} color="#7A5BA8">VENTAS DE HOY</Texto>
        <Texto size={150} weight={900} color={INK}>$0</Texto>
        <Texto size={26} weight={600} color="#7A5BA8">· · · · · · · · · · ·</Texto>
      </Papelito>
    </Pieza>
    <Pieza at={ws(10)} until={T.c2} x={570} y={170} w={460} h={230} rot={5} seed={3}>
      <Papelito w={460} h={230} seed={8}>
        <Texto size={30} weight={700} color="#7A5BA8">TUS REDES</Texto>
        <Texto size={64} weight={900}>❤ 0 · 💬 0</Texto>
      </Papelito>
      <Cinta x={150} y={-24} rot={3} />
    </Pieza>
    <Garabato at={ws(11) + 0.2} until={T.c2} shape="circle" x={40} y={210} w={260} h={200} width={12} seed={3} />
    <Garabato at={ws(20)} until={T.c2} shape="arrow" x={300} y={460} w={180} h={250} color="#F4F1EC" width={10} />
    <Garabato at={ws(21)} until={T.c2} shape="bang" x={900} y={600} w={110} h={170} width={16} />

    {/* S3 · no es que no funcionen / mala manera */}
    <Garabato at={ws(29) + 0.25} until={ws(30) - 0.04} shape="strike" x={150} y={420} w={860} h={80} color="#F4F1EC" width={13} draw={7} />
    <Garabato at={ws(38)} until={T.c3} shape="circle" x={150} y={1610} w={900} h={170} width={11} seed={7} />

    {/* S4 · realidad que todo el mundo desconoce */}
    <Garabato at={ws(43)} until={T.c4} shape="sparkle" x={110} y={520} w={120} h={120} color="#F4F1EC" width={8} />
    <Garabato at={ws(43) + 0.15} until={T.c4} shape="sparkle" x={870} y={600} w={90} h={90} color={PURPLE} width={8} />
    <Sello at={ws(48)} until={T.c4} x={540} y={330} text="DESCONOCE" size={96} rot={-8} />

    {/* S5 · el cliente entra a tu perfil… pasa al siguiente comercio */}
    <Pieza at={ws(50)} until={ws(74) - 0.05} x={40} y={110} w={620} h={400} rot={-3} seed={5} from="left">
      <Rasgado w={620} h={400} seed={6}>
        <BVid src="broll/b8_scroll.mp4" from={ws(50)} />
      </Rasgado>
      <Cinta x={220} y={-24} rot={-6} />
    </Pieza>
    <Pieza at={ws(57)} until={T.c5} x={40} y={560} w={360} h={560} rot={4} seed={9}>
      <Papelito w={360} h={560} seed={12}>
        <div style={{display: 'flex', alignItems: 'center', gap: 14}}>
          <div style={{width: 64, height: 64, borderRadius: 32, background: '#C9B8E0'}} />
          <Texto size={30}>@tunegocio</Texto>
        </div>
        <div style={{display: 'grid', gridTemplateColumns: 'repeat(3, 88px)', gap: 8, marginTop: 22}}>
          {Array.from({length: 9}, (_, i) => (
            <div key={i} style={{height: 88, background: i % 2 ? '#DCD3E8' : '#CFC3DF'}} />
          ))}
        </div>
        <Texto size={30} weight={700} color="#7A5BA8">
          <div style={{marginTop: 18}}>0 ventas este mes</div>
        </Texto>
      </Papelito>
    </Pieza>
    <Garabato at={ws(67)} until={T.c5} shape="cross" x={60} y={640} w={320} h={420} width={18} draw={7} />
    <Pieza at={ws(74)} until={T.c5} x={120} y={130} w={640} h={400} rot={4} seed={13} from="right">
      <Rasgado w={640} h={400} seed={14}>
        <BVid src="broll/b8_tienda_ropa.mp4" from={ws(74)} />
      </Rasgado>
      <Cinta x={40} y={-20} rot={-14} />
      <Cinta x={460} y={-20} rot={10} />
    </Pieza>
    <Garabato at={ws(74) + 0.15} until={T.c5} shape="arrowR" x={300} y={500} w={300} h={170} color="#F4F1EC" width={10} rot={-20} />

    {/* S6 · te escribe y ni siquiera le contestas */}
    <Pieza at={ws(83)} until={T.c6} x={60} y={150} w={560} h={230} rot={-5} seed={15}>
      <Papelito w={560} h={230} seed={16}>
        <Texto size={36} weight={700} color="#7A5BA8">Hola 👋</Texto>
        <Texto size={56} weight={900}>¿Cuánto cuesta?</Texto>
        <Texto size={24} weight={600} color="#9A90A8">Visto · 14:32</Texto>
      </Papelito>
    </Pieza>
    <Sello at={ws(89)} until={T.c6} x={390} y={320} text="SIN RESPUESTA" size={62} rot={8} />

    {/* S7 · ocupados en el día a día · todólogo */}
    <Pieza at={T.c6 + 0.3} until={T.c7} x={30} y={110} w={500} h={310} rot={-4} seed={17}>
      <Rasgado w={500} h={310} seed={18}>
        <BVid src="broll/b8_tendero.mp4" from={T.c6 + 0.3} />
      </Rasgado>
      <Cinta x={170} y={-22} />
    </Pieza>
    <Pieza at={ws(99)} until={T.c7} x={570} y={90} w={300} h={470} rot={5} seed={19}>
      <Rasgado w={300} h={470} seed={20}>
        <BVid src="broll/b8_barbero.mp4" from={ws(99)} />
      </Rasgado>
      <Cinta x={70} y={-22} rot={6} />
    </Pieza>
    <Pieza at={ws(105)} until={T.c7} x={130} y={450} w={300} h={460} rot={-6} seed={21}>
      <Rasgado w={300} h={460} seed={22}>
        <BVid src="broll/b8_empaque.mp4" from={ws(105)} />
      </Rasgado>
      <Cinta x={60} y={-22} rot={-10} />
    </Pieza>
    <Garabato at={ws(112)} until={T.c7} shape="circle" x={0} y={60} w={1000} h={900} width={14} seed={11} draw={9} />
    <Pieza at={ws(112) + 0.25} until={T.c7} x={560} y={640} w={470} h={150} rot={-4} seed={23}>
      <Papelito w={470} h={150} seed={24} tint="#EADCFF">
        <Texto size={46} weight={900}>¡todo lo haces tú! 😩</Texto>
      </Papelito>
    </Pieza>

    {/* S8 · equipo de marketing · por ti */}
    <Pieza at={ws(125)} until={T.c8} x={60} y={100} w={600} h={380} rot={4} seed={25}>
      <Rasgado w={600} h={380} seed={26}>
        <BVid src="broll/b8_equipo.mp4" from={ws(125)} />
      </Rasgado>
      <Cinta x={210} y={-24} rot={-3} />
    </Pieza>
    <Garabato at={ws(130)} until={T.c8} shape="underline" x={290} y={1700} w={560} h={70} width={12} draw={7} />

    {/* S9 · Grow Marketing · expertos · estrategia · vamos a tu negocio */}
    <Pieza at={ws(136)} until={T.c9} x={230} y={110} w={620} h={270} rot={-3} seed={27}>
      <Rasgado w={620} h={270} seed={28}>
        <AbsoluteFill style={{background: '#120A1A', display: 'grid', placeItems: 'center'}}>
          <Img src={staticFile('img/logo_grow.png')} style={{width: 520}} />
        </AbsoluteFill>
      </Rasgado>
      <Cinta x={-30} y={20} rot={-40} />
      <Cinta x={500} y={10} rot={36} />
    </Pieza>
    <Garabato at={ws(137) + 0.2} until={T.c9} shape="sparkle" x={110} y={80} w={110} h={110} color="#F4F1EC" width={8} />
    <Garabato at={ws(139)} until={T.c9} shape="star" x={870} y={90} w={140} h={140} width={9} />
    <Pieza at={ws(144)} until={T.c9} x={30} y={520} w={270} h={200} rot={-6} seed={29}>
      <Papelito w={270} h={200} seed={30} tint="#EADCFF">
        <Texto size={40} weight={900}>ESTRATEGIA</Texto>
        <Texto size={60} weight={900} color={PURPLE}>✓</Texto>
      </Papelito>
    </Pieza>
    <Pieza at={ws(150)} until={T.c9} x={790} y={560} w={270} h={130} rot={6} seed={31}>
      <Papelito w={270} h={130} seed={32}>
        <Texto size={38} weight={900}>📍 tu negocio</Texto>
      </Papelito>
    </Pieza>

    {/* S10 · grabamos contenido · tomamos fotos · lo más importante */}
    <Pieza at={ws(151)} until={T.c10} x={40} y={110} w={600} h={360} rot={-3} seed={33}>
      <Rasgado w={600} h={360} seed={34}>
        <BVid src="broll/b8_grabando.mp4" from={ws(151)} />
      </Rasgado>
      <Cinta x={210} y={-22} />
    </Pieza>
    <Garabato at={ws(152) + 0.2} until={T.c10} shape="check" x={670} y={170} w={130} h={130} color="#F4F1EC" width={13} />
    <Pieza at={ws(156)} until={T.c10} x={380} y={470} w={620} h={380} rot={4} seed={35}>
      <Rasgado w={620} h={380} seed={36}>
        <BVid src="broll/b8_foto.mp4" from={ws(156)} />
      </Rasgado>
      <Cinta x={230} y={-22} rot={5} />
    </Pieza>
    <Garabato at={ws(157) + 0.4} until={T.c10} shape="check" x={90} y={560} w={130} h={130} color="#F4F1EC" width={13} />
    <Garabato at={ws(161)} until={T.c10} shape="star" x={110} y={960} w={210} h={210} width={10} />

    {/* S11 · 100 % profesionales */}
    <Garabato at={ws(165) + 0.4} until={T.end} shape="circle" x={290} y={1450} w={540} h={230} width={12} seed={5} />
    <Garabato at={ws(167)} until={T.end} shape="sparkle" x={120} y={1380} w={120} h={120} color="#F4F1EC" width={8} />
    <Garabato at={ws(167) + 0.15} until={T.end} shape="sparkle" x={880} y={1500} w={90} h={90} color={PURPLE} width={8} />
  </>
);

// ---------------------------------------------------------------- cierre
export const Cierre: React.FC = () => {
  const frame = useCurrentFrame();
  if (frame < T.end * F) return null;
  const l = frame - T.end * F;
  const fade = interpolate(frame, [(TOTAL - 0.4) * F, TOTAL * F], [0, 1], clamp);
  const jt = jitter(frame, 2, 0.5);
  return (
    <>
      <AbsoluteFill style={{filter: OUTLINE, translate: `0 ${interpolate(l, [0, 8], [40, 130], {...clamp, easing: easeOut})}px`, scale: '0.8', transformOrigin: '50% 100%', rotate: `${-2 + jt.r}deg`}}>
        <LastFrame mask="c" local={8} />
      </AbsoluteFill>
      <TiraPapel top={1660} />
      <Pieza at={T.end + 0.1} until={TOTAL + 1} x={190} y={220} w={700} h={300} rot={-2} seed={41}>
        <Rasgado w={700} h={300} seed={42}>
          <AbsoluteFill style={{background: '#120A1A', display: 'grid', placeItems: 'center'}}>
            <Img src={staticFile('img/logo_grow.png')} style={{width: 590}} />
          </AbsoluteFill>
        </Rasgado>
        <Cinta x={-30} y={30} rot={-40} />
        <Cinta x={580} y={20} rot={36} />
      </Pieza>
      <Pieza at={T.end + 0.5} until={TOTAL + 1} x={200} y={590} w={680} h={130} rot={3} seed={43}>
        <Papelito w={680} h={130} seed={44} tint="#EADCFF">
          <div style={{fontFamily: OUTFIT, fontSize: 46, fontWeight: 900, color: INK}}>tu equipo de marketing 💜</div>
        </Papelito>
      </Pieza>
      <Garabato at={T.end + 0.9} until={TOTAL + 1} shape="sparkle" x={110} y={170} w={110} h={110} color="#F4F1EC" width={8} />
      <Garabato at={T.end + 1.0} until={TOTAL + 1} shape="star" x={880} y={520} w={130} h={130} width={9} />
      <AbsoluteFill style={{background: '#000', opacity: fade}} />
    </>
  );
};

export {MODOS, TITLES};
