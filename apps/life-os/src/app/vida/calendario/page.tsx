import type { Metadata } from "next";
import { CalendarPage } from "@/components/life/calendar";

export const metadata: Metadata = { title: "Calendario" };

export default function Page() {
  return <CalendarPage />;
}
