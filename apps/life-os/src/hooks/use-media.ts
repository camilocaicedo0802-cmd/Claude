"use client";

import * as React from "react";

export function useMediaQuery(query: string, fallback = false): boolean {
  const subscribe = React.useCallback(
    (cb: () => void) => {
      const mq = window.matchMedia(query);
      mq.addEventListener("change", cb);
      return () => mq.removeEventListener("change", cb);
    },
    [query],
  );
  return React.useSyncExternalStore(
    subscribe,
    () => window.matchMedia(query).matches,
    () => fallback,
  );
}

export const useIsDesktop = () => useMediaQuery("(min-width: 1024px)");
