import type { ReactNode } from "react";
import { RevealText } from "./RevealText";

/** Section title: white Poppins with one Playfair italic word, printed line by line. */
export function SectionHeading({ lines, id, className = "" }: { lines: ReactNode[]; id?: string; className?: string }) {
  return <RevealText as="h2" id={id} lines={lines} className={`title ${className}`} />;
}
