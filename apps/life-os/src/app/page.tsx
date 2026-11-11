"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { PageSkeleton } from "@/components/shared/primitives";

/** The app opens on "Mi día": the most urgent things from the three areas. */
export default function Home() {
  const router = useRouter();
  React.useEffect(() => {
    router.replace("/vida/");
  }, [router]);
  return <PageSkeleton />;
}
