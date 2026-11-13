import type { Metadata } from "next";
import { PlannerPage } from "@/components/life/planner";

export const metadata: Metadata = { title: "Planificador" };

export default function Page() {
  return <PlannerPage />;
}
