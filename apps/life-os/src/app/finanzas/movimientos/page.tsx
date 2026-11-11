import type { Metadata } from "next";
import { MovementsPage } from "@/components/finance/movements";

export const metadata: Metadata = { title: "Movimientos" };

export default function Page() {
  return <MovementsPage />;
}
