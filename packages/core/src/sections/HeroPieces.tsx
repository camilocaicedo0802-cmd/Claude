import { pieceSmallSrc } from "../content/media";
import type { ImageAsset } from "../content/types";

/** Two real pieces peeking out from behind the hero video (designer site, large screens only). */
export function HeroPieces({ pieces }: { pieces: ImageAsset[] }) {
  const [a, b] = pieces;
  return (
    <div aria-hidden className="pointer-events-none absolute inset-0 hidden lg:block">
      {a && (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={pieceSmallSrc(a.file)}
          alt=""
          className="absolute -left-[46%] top-[6%] w-[52%] opacity-90 shadow-[0_24px_60px_rgba(0,0,0,0.6)]"
        />
      )}
      {b && (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={pieceSmallSrc(b.file)}
          alt=""
          className="absolute -left-[30%] bottom-[4%] w-[44%] opacity-90 shadow-[0_24px_60px_rgba(0,0,0,0.6)]"
        />
      )}
    </div>
  );
}
