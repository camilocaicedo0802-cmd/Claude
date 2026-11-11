import type { Metadata } from "next";
import { AnalysisPage } from "@/components/finance/analysis";

export const metadata: Metadata = { title: "Análisis" };

export default function Page() {
  return <AnalysisPage />;
}
