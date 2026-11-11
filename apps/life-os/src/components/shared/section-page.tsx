"use client";

import * as React from "react";
import { NAV } from "@/components/shell/nav";
import { PageHeader, SectionTabs } from "./primitives";

export function SectionPage({
  section,
  title,
  description,
  actions,
  children,
}: {
  section: "finanzas" | "clientes" | "vida";
  title: React.ReactNode;
  description?: React.ReactNode;
  actions?: React.ReactNode;
  children: React.ReactNode;
}) {
  const nav = NAV.find((n) => n.key === section)!;
  return (
    <div className="space-y-5 lg:space-y-6">
      <div className="space-y-4">
        <PageHeader title={title} description={description} actions={actions} />
        <div className="lg:hidden">
          <SectionTabs items={nav.items} />
        </div>
      </div>
      <div className="animate-rise space-y-5 lg:space-y-6">{children}</div>
    </div>
  );
}
