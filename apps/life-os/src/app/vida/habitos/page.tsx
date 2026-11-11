import type { Metadata } from "next";
import { HabitsPage } from "@/components/life/habits";

export const metadata: Metadata = { title: "Hábitos" };

export default function Page() {
  return <HabitsPage />;
}
