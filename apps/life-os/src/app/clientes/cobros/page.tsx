import type { Metadata } from "next";
import { CollectionsPage } from "@/components/clients/collections";

export const metadata: Metadata = { title: "Cobros" };

export default function Page() {
  return <CollectionsPage />;
}
