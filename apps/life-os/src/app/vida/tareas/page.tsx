import type { Metadata } from "next";
import { TasksPage } from "@/components/life/tasks";

export const metadata: Metadata = { title: "Tareas" };

export default function Page() {
  return <TasksPage />;
}
