import type { Metadata } from "next";
import { ClientsOverview } from "@/components/clients/overview";

export const metadata: Metadata = { title: "Clientes" };

export default function Page() {
  return <ClientsOverview />;
}
