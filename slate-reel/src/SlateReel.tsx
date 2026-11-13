import { Audio } from "@remotion/media";
import React from "react";
import { AbsoluteFill, interpolate, Sequence, staticFile, Track } from "remotion";
import { CalendarBar, Cascade, EndCard, GlowEdges, NumberedItem, RatingBar, Subtitles, Word } from "./components/Graphics";
import { BRoll, TalkingShot } from "./components/Shots";
import { BRAND, C } from "./theme";

/**
 * SLATE · Holiday spray tan (Tulsa) — 1080×1920 @ 30 fps, 657 fotogramas (21.9 s).
 * Todos los tiempos están en fotogramas de la composición y salen de la
 * transcripción Whisper de la voz montada (analysis/voice_words.json),
 * afinados con la energía de la voz. Reglas de estilo: estilo.md.
 */
export const SLATE_REEL_DURATION = 657;

const raw = (n: string) => staticFile(`raw/${n}.mp4`);
const broll = (n: string) => staticFile(`broll/${n}.mp4`);
const sfx = (n: string) => staticFile(`sfx/${n}.wav`);

export const SlateReel: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      {/* ───────────── Tomas a cámara (llevan la voz) ───────────── */}
      <Track name="A cámara">
        <TalkingShot
          name="Hook · fachada SLATE"
          src={raw("IMG_7055")}
          from={0}
          durationInFrames={112}
          trimBefore={68}
          focus={[0.45, 0.46]}
          focusTrack={[
            [0, 0.325, 0.545],
            [4, 0.348, 0.54],
            [10, 0.376, 0.532],
            [16, 0.391, 0.525],
            [22, 0.402, 0.509],
            [34, 0.406, 0.498],
            [40, 0.411, 0.488],
            [52, 0.433, 0.475],
            [64, 0.433, 0.462],
            [76, 0.448, 0.458],
            [88, 0.469, 0.444],
            [100, 0.491, 0.441],
            [112, 0.489, 0.432],
          ]}
          target={[0.5, 0.3]}
          zoom={[
            [0, 2.3],
            [18, 1.85],
            [43, 1.9],
            [44, 2.1],
            [58, 2.12],
            [88, 1.72],
            [89, 1.85],
            [112, 1.88],
          ]}
        />
        <TalkingShot
          name="Thanksgiving · recepción"
          src={raw("IMG_7058")}
          from={112}
          durationInFrames={47}
          trimBefore={24}
          focus={[0.545, 0.448]}
          target={[0.5, 0.31]}
          zoom={[
            [0, 1.75],
            [47, 1.8],
          ]}
        />
        <TalkingShot
          name="Christmas / New Year's · recepción"
          src={raw("IMG_7059")}
          from={159}
          durationInFrames={85}
          trimBefore={77}
          focus={[0.5, 0.49]}
          target={[0.5, 0.32]}
          zoom={[
            [0, 1.65],
            [45, 1.7],
          ]}
        />
        <TalkingShot
          name="Tip · banco"
          src={raw("IMG_7061")}
          from={244}
          durationInFrames={136}
          trimBefore={64}
          focus={[0.56, 0.33]}
          target={[0.5, 0.28]}
          zoom={[
            [0, 1.55],
            [86, 1.58],
            [87, 1.88],
            [136, 1.9],
          ]}
        />
        <TalkingShot
          name="Develop · estantería"
          src={raw("IMG_7062")}
          from={380}
          durationInFrames={61}
          trimBefore={20}
          focus={[0.49, 0.35]}
          target={[0.5, 0.3]}
          zoom={[
            [0, 1.5],
            [61, 1.55],
          ]}
        />
        <TalkingShot
          name="Booking up fast · estantería"
          src={raw("IMG_7063")}
          from={441}
          durationInFrames={156}
          trimBefore={29}
          focus={[0.52, 0.37]}
          target={[0.5, 0.3]}
          zoom={[
            [0, 1.28],
            [50, 1.31],
            [51, 1.56],
            [64, 1.56],
            [65, 1.3],
            [116, 1.31],
            [117, 1.42],
            [156, 1.47],
          ]}
        />
      </Track>

      {/* ───────────── B-roll (sin sonido) ───────────── */}
      <Track name="B-roll">
        <BRoll name="love a good spray tan" src={broll("hook_spray_face")} from={59} durationInFrames={30} trimBefore={9} />
        <BRoll name="Christmas parties" src={broll("xmas_arms_up")} from={204} durationInFrames={29} trimBefore={26} />
        <BRoll name="New Year's" src={broll("newyear_result")} from={230} durationInFrames={32} trimBefore={18} fadeIn={3} />
        <BRoll name="book your spray tan" src={broll("book_slate_gun")} from={293} durationInFrames={27} trimBefore={9} />
        <BRoll name="fully develop" src={broll("develop_tanline")} from={417} durationInFrames={24} trimBefore={27} />
        <BRoll name="Resultado 1" src={broll("result_strap")} from={506} durationInFrames={17} trimBefore={9} fadeIn={3} />
        <BRoll name="Resultado 2" src={broll("result_smile_tanline")} from={523} durationInFrames={17} trimBefore={9} fadeIn={0} />
        <BRoll name="Resultado 3" src={broll("result_glow_face")} from={540} durationInFrames={18} trimBefore={9} fadeIn={0} />
      </Track>

      {/* ───────────── Halo en bordes (colores de marca) ───────────── */}
      <Track name="Halo">
        <GlowEdges name="Halo salvia · 2 days" from={331} durationInFrames={26} rgb={C.glowSage} peak={0.5} />
        <GlowEdges name="Halo marrón · fast" from={491} durationInFrames={15} rgb={C.glowBrown} peak={0.42} blend="normal" />
        <GlowEdges name="Halo beige · glow" from={577} durationInFrames={18} rgb={C.glowBeige} peak={0.45} />
      </Track>

      {/* ───────────── Títulos (base Inter Display · palabras clave con fuentes de marca) ───────────── */}
      <Track name="Títulos">
        <Cascade name="Hook · Tulsa, OK" from={0} durationInFrames={58}>
          <Word at={2} x={110} y={900} size={150} typing={2}>
            Tulsa,
          </Word>
          <Word at={16} x={520} y={990} size={230} font="brand" color={C.highlight}>
            OK
          </Word>
        </Cascade>
        <Cascade name="Hook · Spray tan lovers" from={66} durationInFrames={23}>
          <Word at={0} x={110} y={930} size={120}>
            Spray tan
          </Word>
          <Word at={6} x={390} y={1045} size={175} font="brand">
            lovers,
          </Word>
        </Cascade>
        <Cascade name="Hook · this is for you" from={90} durationInFrames={22}>
          <Word at={0} x={170} y={930} size={120}>
            this is
          </Word>
          <Word at={10} x={300} y={1045} size={190} font="brand" color={C.highlight}>
            for you
          </Word>
        </Cascade>
        <NumberedItem
          name="1. Thanksgiving"
          from={114}
          durationInFrames={45}
          num="1."
          left={150}
          lines={[
            { text: "Thanksgiving", at: 2 },
            { text: "is only a week away", at: 9 },
          ]}
        />
        <NumberedItem
          name="2. Christmas parties"
          from={204}
          durationInFrames={26}
          num="2."
          left={200}
          lines={[
            { text: "Christmas", at: 2 },
            { text: "parties", at: 7 },
          ]}
        />
        <NumberedItem name="3. New Year's" from={230} durationInFrames={18} num="3." left={200} lines={[{ text: "New Year's", at: 2 }]} />
        <Cascade name="Tip · etiqueta (tecleada)" from={250} durationInFrames={128}>
          <Word at={0} x={0} y={850} size={50} weight={600} align="center" typing={1.5}>
            Spray tan tip
          </Word>
        </Cascade>
        <Cascade name="Tip · 2 days before your event" from={320} durationInFrames={58}>
          <Word at={0} x={0} y={955} size={124} font="brand" color={C.highlight} align="center">
            2 days before
          </Word>
          <Word at={42} x={0} y={1112} size={64} weight={500} align="center">
            your event
          </Word>
        </Cascade>
        <Cascade name="Holiday spots are filling up (tecleado)" from={443} durationInFrames={63}>
          <Word at={0} x={0} y={960} size={64} weight={500} align="center" typing={1.4}>
            Holiday spots
          </Word>
          <Word at={23} x={0} y={1030} size={64} weight={500} align="center" typing={1.4}>
            are filling up!
          </Word>
        </Cascade>
        <Cascade name="CTA · Book your holiday glow" from={558} durationInFrames={39}>
          <Word at={0} x={0} y={950} size={64} weight={500} align="center" typing={2}>
            Book your
          </Word>
          <Word at={8} x={95} y={1035} size={140} font="brand" color={C.highlight}>
            holiday
          </Word>
          <Word at={20} x={690} y={1005} size={190} font="script" color={BRAND.beige}>
            glow
          </Word>
        </Cascade>
      </Track>

      <Track name="Barras">
        <CalendarBar
          name="Calendario · 2 días antes"
          from={322}
          durationInFrames={56}
          y={1290}
          eventIndex={5}
          targetIndex={3}
          arriveAt={11}
          pointer={[
            [0, 5],
            [4, 5],
            [7, 4],
            [8, 4],
            [11, 3],
          ]}
        />
        <RatingBar
          name="Disponibilidad · se llena"
          from={452}
          durationInFrames={54}
          y={1180}
          pointer={[
            [0, 2],
            [19, 2],
            [22, 3],
            [25, 4],
            [28, 5],
            [31, 6],
            [34, 7],
            [37, 8],
            [40, 9],
          ]}
        />
      </Track>

      {/* ───────────── Subtítulos palabra a palabra (Whisper) ───────────── */}
      <Subtitles
        name="Subtítulos"
        captions={[
          { text: "And", startMs: 5367, endMs: 5633, timestampMs: 5367, confidence: null },
          { text: " then", startMs: 5633, endMs: 5767, timestampMs: 5633, confidence: null, pageBreakAfter: true },
          { text: "we're", startMs: 5767, endMs: 6067, timestampMs: 5767, confidence: null },
          { text: " heading", startMs: 6067, endMs: 6267, timestampMs: 6067, confidence: null, pageBreakAfter: true },
          { text: "straight", startMs: 6267, endMs: 6467, timestampMs: 6267, confidence: null },
          { text: " into", startMs: 6467, endMs: 6800, timestampMs: 6467, confidence: null, pageBreakAfter: true },
          { text: "And", startMs: 8267, endMs: 8333, timestampMs: 8200, confidence: null },
          { text: " remember", startMs: 8333, endMs: 8667, timestampMs: 8333, confidence: null, pageBreakAfter: true },
          { text: "to", startMs: 8667, endMs: 9200, timestampMs: 8667, confidence: null },
          { text: " make", startMs: 9200, endMs: 9333, timestampMs: 9200, confidence: null },
          { text: " sure", startMs: 9333, endMs: 9533, timestampMs: 9333, confidence: null, pageBreakAfter: true },
          { text: "you", startMs: 9533, endMs: 9767, timestampMs: 9533, confidence: null },
          { text: " book", startMs: 9767, endMs: 9900, timestampMs: 9767, confidence: null, pageBreakAfter: true },
          { text: "your", startMs: 9900, endMs: 10000, timestampMs: 9900, confidence: null },
          { text: " spray", startMs: 10000, endMs: 10133, timestampMs: 10000, confidence: null },
          { text: " tan", startMs: 10133, endMs: 10667, timestampMs: 10133, confidence: null, pageBreakAfter: true },
          { text: "so", startMs: 12733, endMs: 12800, timestampMs: 12733, confidence: null },
          { text: " your", startMs: 12800, endMs: 12967, timestampMs: 12800, confidence: null },
          { text: " tan", startMs: 12967, endMs: 13233, timestampMs: 12967, confidence: null, pageBreakAfter: true },
          { text: "has", startMs: 13233, endMs: 13533, timestampMs: 13233, confidence: null },
          { text: " time", startMs: 13533, endMs: 13800, timestampMs: 13533, confidence: null, pageBreakAfter: true },
          { text: "to", startMs: 13800, endMs: 13933, timestampMs: 13800, confidence: null },
          { text: " fully", startMs: 13933, endMs: 14200, timestampMs: 13933, confidence: null, pageBreakAfter: true },
          { text: "develop.", startMs: 14200, endMs: 14700, timestampMs: 14200, confidence: null, pageBreakAfter: true },
          { text: "so", startMs: 16867, endMs: 16967, timestampMs: 16867, confidence: null },
          { text: " make", startMs: 16967, endMs: 17267, timestampMs: 16967, confidence: null },
          { text: " sure", startMs: 17267, endMs: 17467, timestampMs: 17267, confidence: null, pageBreakAfter: true },
          { text: "to", startMs: 17467, endMs: 17700, timestampMs: 17467, confidence: null },
          { text: " book", startMs: 17700, endMs: 18000, timestampMs: 17700, confidence: null, pageBreakAfter: true },
          { text: "your", startMs: 18000, endMs: 18100, timestampMs: 18000, confidence: null },
          { text: " appointment", startMs: 18100, endMs: 18533, timestampMs: 18100, confidence: null, pageBreakAfter: true },
        ]}
      />

      {/* ───────────── Cierre: panel salvia + logotipo del manual ───────────── */}
      <Sequence name="Cierre · logo SLATE" from={591} durationInFrames={66}>
        <EndCard durationInFrames={66} />
      </Sequence>

      {/* ───────────── Música (Higgsfield · ElevenLabs Music v2) ───────────── */}
      <Audio
        name="Música"
        src={staticFile("music/music_v1.mp3")}
        durationInFrames={657}
        volume={(f) => interpolate(f, [0, 585, 600], [0.13, 0.13, 0.32], { extrapolateRight: "clamp" })}
      />

      {/* ───────────── SFX (pack 1, ver estilo.md §8 y §10) ───────────── */}
      <Track name="SFX · typing (textos tecleados)">
        <Audio name="Typing · Tulsa," src={sfx("typing_short")} from={2} volume={0.35} />
        <Audio name="Typing · Spray tan tip" src={sfx("typing_long")} from={250} volume={0.3} />
        <Audio name="Typing · Holiday spots" src={sfx("typing_long")} from={443} volume={0.3} />
        <Audio name="Typing · are filling up!" src={sfx("typing_long")} from={466} volume={0.3} />
        <Audio name="Typing · Book your" src={sfx("typing_short")} from={558} volume={0.3} />
      </Track>
      <Track name="SFX · pop (entrada de textos)">
        <Audio name="Pop · for you" src={sfx("pop")} from={98} volume={0.2} />
        <Audio name="Pop · 1. Thanksgiving" src={sfx("pop")} from={114} volume={0.22} />
        <Audio name="Pop · 2. Christmas" src={sfx("pop")} from={204} volume={0.22} />
        <Audio name="Pop · 3. New Year's" src={sfx("pop")} from={230} volume={0.22} />
        <Audio name="Pop · 2 days before" src={sfx("pop")} from={320} volume={0.16} />
        <Audio name="Pop · 10" src={sfx("pop")} from={492} volume={0.22} />
        <Audio name="Pop · logo" src={sfx("pop")} from={595} volume={0.14} />
      </Track>
      <Track name="SFX · tecla (puntero del calendario)">
        <Audio name="Tecla · paso 1" src={sfx("tecla")} from={329} volume={0.2} />
        <Audio name="Tecla · paso 2" src={sfx("tecla")} from={333} volume={0.2} />
      </Track>
      <Track name="SFX · swoosh / sub drop (halo y hook)">
        <Audio name="Sub drop · OK" src={sfx("sub_drop")} from={16} volume={0.28} />
        <Audio name="Swoosh · halo 2 days" src={sfx("swoosh_05")} from={331} volume={0.3} />
        <Audio name="Swoosh · halo fast" src={sfx("swoosh_04")} from={490} volume={0.36} />
        <Audio name="Swoosh · glow" src={sfx("swoosh_03")} from={576} volume={0.28} />
      </Track>
    </AbsoluteFill>
  );
};
