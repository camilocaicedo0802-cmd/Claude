import { Composition } from "remotion";
import { Edicion } from "./Edicion";
import { DURACION_TOTAL_S } from "./plan";
import { FPS } from "./estilo";
import { V1, V1_DURACION } from "./lote2/V1";
import { V2, V2_DURACION } from "./lote2/V2";
import { V3, V3_DURACION } from "./lote2/V3";

// Proyecto vertical 1080x1920 a 60 fps
export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition id="Farmasi" component={Edicion} durationInFrames={Math.round(DURACION_TOTAL_S * FPS)} fps={FPS} width={1080} height={1920} />
      <Composition id="L2V1" component={V1} durationInFrames={Math.round(V1_DURACION * FPS)} fps={FPS} width={1080} height={1920} />
      <Composition id="L2V2" component={V2} durationInFrames={Math.round(V2_DURACION * FPS)} fps={FPS} width={1080} height={1920} />
      <Composition id="L2V3" component={V3} durationInFrames={Math.round(V3_DURACION * FPS)} fps={FPS} width={1080} height={1920} />
    </>
  );
};
