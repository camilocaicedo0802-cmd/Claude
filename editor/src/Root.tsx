import { MyComposition } from "./Composition";
import { Dia2 } from "./dia2/Dia2";
import { Dia3 } from "./dia3/Dia3";
import { Dia4 } from "./dia4/Dia4";
import { Dia5 } from "./dia5/Dia5";
import { Dia6 } from "./dia6/Dia6";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* Día 1 (entregado) */}
      <MyComposition />
      {/* Día 2 · Punto de partida */}
      <Dia2 />
      {/* Día 3 · Preparación y uso seguro */}
      <Dia3 />
      {/* Días 4 y 5 · rutinas con voz en off sobre el mismo crudo largo */}
      <Dia4 />
      <Dia5 />
      {/* Día 6 · Piernas y apariencia de la celulitis (rutina con voz en off sobre su propio crudo) */}
      <Dia6 />
    </>
  );
};
