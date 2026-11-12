import type { Metadata } from "next";
import { TrackerPage } from "@/components/life/tracker";

export const metadata: Metadata = { title: "Tareas" };

export default function Page() {
  return <TrackerPage />;
}
