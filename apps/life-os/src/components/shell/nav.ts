import { Sunrise, Users, Wallet, type LucideIcon } from "lucide-react";
import type { SubNavItem } from "@/components/shared/primitives";

export interface NavSection {
  key: "finanzas" | "clientes" | "vida";
  label: string;
  href: string;
  icon: LucideIcon;
  items: SubNavItem[];
}

export const NAV: NavSection[] = [
  {
    key: "finanzas",
    label: "Finanzas",
    href: "/finanzas/",
    icon: Wallet,
    items: [
      { href: "/finanzas/", label: "Resumen", exact: true },
      { href: "/finanzas/movimientos/", label: "Movimientos" },
      { href: "/finanzas/obligaciones/", label: "Pagos" },
      { href: "/finanzas/presupuestos/", label: "Presupuestos" },
      { href: "/finanzas/cuentas/", label: "Cuentas" },
      { href: "/finanzas/analisis/", label: "Análisis" },
      { href: "/finanzas/metas/", label: "Metas" },
    ],
  },
  {
    key: "clientes",
    label: "Clientes",
    href: "/clientes/",
    icon: Users,
    items: [
      { href: "/clientes/", label: "Resumen", exact: true },
      { href: "/clientes/trabajos/", label: "Trabajos" },
      { href: "/clientes/cobros/", label: "Cobros" },
    ],
  },
  {
    key: "vida",
    label: "Mi Vida",
    href: "/vida/",
    icon: Sunrise,
    items: [
      { href: "/vida/", label: "Mi día", exact: true },
      { href: "/vida/tareas/", label: "Tareas" },
      { href: "/vida/calendario/", label: "Calendario" },
      { href: "/vida/semana/", label: "Semana" },
      { href: "/vida/habitos/", label: "Hábitos" },
    ],
  },
];

export function sectionFor(pathname: string): NavSection | undefined {
  return NAV.find((s) => pathname.startsWith(s.href.replace(/\/$/, "")));
}
