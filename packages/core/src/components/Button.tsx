"use client";
import { motion, useMotionValue, useReducedMotion, useSpring } from "motion/react";
import type { AnchorHTMLAttributes, ReactNode } from "react";
import { useRef } from "react";
import { useFinePointer } from "../lib/media-query";

type Variant = "primary" | "ghost";

interface Props extends Omit<AnchorHTMLAttributes<HTMLAnchorElement>, "onDrag" | "onDragStart" | "onDragEnd" | "onAnimationStart"> {
  href: string;
  children: ReactNode;
  variant?: Variant;
  size?: "md" | "lg";
  icon?: ReactNode;
  magnetic?: boolean;
}

const base =
  "press group relative inline-flex select-none items-center justify-center gap-3 whitespace-nowrap font-medium uppercase tracking-[0.06em]";
const variants: Record<Variant, string> = {
  primary: "bg-signal text-paper hover:bg-signal-deep",
  ghost: "border border-white/25 text-paper hover:border-paper",
};
const sizes = { md: "h-12 px-6 text-[0.8125rem]", lg: "h-16 px-8 text-[0.9375rem] md:h-[72px] md:px-10 md:text-base" };

/** CTA link. On pointer devices it leans a few pixels toward the cursor. */
export function Button({ href, children, variant = "primary", size = "md", icon, magnetic = false, className = "", ...rest }: Props) {
  const ref = useRef<HTMLAnchorElement>(null);
  const fine = useFinePointer();
  const reduced = useReducedMotion();
  const x = useSpring(useMotionValue(0), { stiffness: 300, damping: 20, mass: 0.4 });
  const y = useSpring(useMotionValue(0), { stiffness: 300, damping: 20, mass: 0.4 });
  const active = magnetic && fine && !reduced;

  return (
    <motion.a
      ref={ref}
      href={href}
      className={`${base} ${variants[variant]} ${sizes[size]} ${className}`}
      style={active ? { x, y } : undefined}
      onPointerMove={(e) => {
        if (!active || !ref.current) return;
        const r = ref.current.getBoundingClientRect();
        x.set(((e.clientX - r.left) / r.width - 0.5) * 12);
        y.set(((e.clientY - r.top) / r.height - 0.5) * 10);
      }}
      onPointerLeave={() => {
        x.set(0);
        y.set(0);
      }}
      {...rest}
    >
      <span>{children}</span>
      {icon && (
        <span aria-hidden className="transition-transform duration-200 ease-[var(--ease-out)] group-hover:-translate-y-0.5 group-hover:translate-x-0.5">
          {icon}
        </span>
      )}
    </motion.a>
  );
}
