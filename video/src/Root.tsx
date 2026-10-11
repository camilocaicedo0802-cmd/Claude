import React from "react";
import { Composition, Folder } from "remotion";
import "./fonts";
import { Main } from "./Main";
import { S01, S01Tiempo } from "./scenes/S01Tiempo";
import { S02, S02Bolsillo } from "./scenes/S02Bolsillo";
import { S03, S03Pantalla } from "./scenes/S03Pantalla";
import { S04, S04Recuperar } from "./scenes/S04Recuperar";
import { S05, S05TuTiempo } from "./scenes/S05TuTiempo";
import { S06, S06Atencion } from "./scenes/S06Atencion";
import { S09, S09Volver } from "./scenes/S09Volver";
import { S11, S11Jamas } from "./scenes/S11Jamas";
import { S12, S12Cierre } from "./scenes/S12Cierre";
import { DURATION_S, FPS, H, W } from "./theme";

const d = (s: { start: number; end: number }) => Math.round((s.end - s.start) * FPS);

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition id="Main" component={Main} durationInFrames={Math.round(DURATION_S * FPS)} fps={FPS} width={W} height={H} />
      <Folder name="Escenas">
        <Composition id="E01-Tiempo" component={S01Tiempo} durationInFrames={d(S01)} fps={FPS} width={W} height={H} />
        <Composition id="E02-Bolsillo" component={S02Bolsillo} durationInFrames={d(S02)} fps={FPS} width={W} height={H} />
        <Composition id="E03-Pantalla" component={S03Pantalla} durationInFrames={d(S03)} fps={FPS} width={W} height={H} />
        <Composition id="E04-Recuperar" component={S04Recuperar} durationInFrames={d(S04)} fps={FPS} width={W} height={H} />
        <Composition id="E05-TuTiempo" component={S05TuTiempo} durationInFrames={d(S05)} fps={FPS} width={W} height={H} />
        <Composition id="E06-Atencion" component={S06Atencion} durationInFrames={d(S06)} fps={FPS} width={W} height={H} />
        <Composition id="E09-Volver" component={S09Volver} durationInFrames={d(S09)} fps={FPS} width={W} height={H} />
        <Composition id="E11-Jamas" component={S11Jamas} durationInFrames={d(S11)} fps={FPS} width={W} height={H} />
        <Composition id="E12-Cierre" component={S12Cierre} durationInFrames={d(S12)} fps={FPS} width={W} height={H} />
      </Folder>
    </>
  );
};
