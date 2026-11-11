import type { Metadata } from "next";
import { WeekPage } from "@/components/life/week";

export const metadata: Metadata = { title: "Semana" };

export default function Page() {
  return <WeekPage />;
}
