import type { Metadata } from "next";
import { AccountsPage } from "@/components/finance/accounts";

export const metadata: Metadata = { title: "Cuentas" };

export default function Page() {
  return <AccountsPage />;
}
