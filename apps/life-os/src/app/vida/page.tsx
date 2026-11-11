import type { Metadata } from "next";
import { TodayPage } from "@/components/life/today";

export const metadata: Metadata = { title: "Mi día" };

export default function Page() {
  return <TodayPage />;
}
