import type { Metadata } from "next";
import { JobsPage } from "@/components/clients/jobs-board";

export const metadata: Metadata = { title: "Trabajos" };

export default function Page() {
  return <JobsPage />;
}
