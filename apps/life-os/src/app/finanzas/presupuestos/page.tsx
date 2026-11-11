import type { Metadata } from "next";
import { BudgetsPage } from "@/components/finance/budgets";

export const metadata: Metadata = { title: "Presupuestos" };

export default function Page() {
  return <BudgetsPage />;
}
