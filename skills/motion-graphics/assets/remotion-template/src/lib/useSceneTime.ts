import { useCurrentFrame, useVideoConfig } from "remotion";

/** Devuelve el tiempo local (s) de la escena y el global (s) del vídeo. */
export const useSceneTime = (start: number) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  return { t, g: start + t, frame, fps };
};
