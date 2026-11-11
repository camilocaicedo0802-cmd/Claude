import type { Metadata } from "next";
import { ObligationsPage } from "@/components/finance/obligations";

export const metadata: Metadata = { title: "Pagos y obligaciones" };

export default function Page() {
  return <ObligationsPage />;
}
