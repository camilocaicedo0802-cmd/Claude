import { Composition } from "remotion";
import { Edicion } from "./Edicion";
import { DURACION_TOTAL_S } from "./plan";
import { FPS } from "./estilo";

// Proyecto vertical 1080x1920 a 60 fps
export const RemotionRoot: React.FC = () => {
  return (
    <Composition id="Farmasi" component={Edicion} durationInFrames={Math.round(DURACION_TOTAL_S * FPS)} fps={FPS} width={1080} height={1920} />
  );
};
