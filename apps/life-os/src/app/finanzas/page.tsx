import type { Metadata } from "next";
import { FinanceOverview } from "@/components/finance/overview";

export const metadata: Metadata = { title: "Finanzas" };

export default function Page() {
  return <FinanceOverview />;
}
