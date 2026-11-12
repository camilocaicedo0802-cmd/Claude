"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import * as Icons from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";
import { useMoney } from "@/hooks/data";
import type { Minor } from "@/lib/money";
import { Skeleton } from "@/components/ui/misc";

// ── Palette tones ────────────────────────────────────────────────────────────

export const PALETTE = ["iris", "emerald", "amber", "rose", "sky", "violet", "teal", "orange", "pink", "slate"] as const;
export type PaletteColor = (typeof PALETTE)[number];

export function toneStyle(color: string | undefined): React.CSSProperties {
  return { "--tone": `var(--c-${PALETTE.includes(color as PaletteColor) ? color : "slate"})` } as React.CSSProperties;
}

export function ColorDot({ color, className }: { color: string; className?: string }) {
  return <span aria-hidden style={toneStyle(color)} className={cn("inline-block size-2 shrink-0 rounded-full tone-dot", className)} />;
}

// ── Icons ────────────────────────────────────────────────────────────────────

const ICONS: Record<string, LucideIcon> = {
  utensils: Icons.Utensils,
  home: Icons.House,
  zap: Icons.Zap,
  bus: Icons.Bus,
  "heart-pulse": Icons.HeartPulse,
  "graduation-cap": Icons.GraduationCap,
  repeat: Icons.Repeat,
  landmark: Icons.Landmark,
  "shopping-bag": Icons.ShoppingBag,
  popcorn: Icons.Popcorn,
  siren: Icons.Siren,
  "circle-dashed": Icons.CircleDashed,
  briefcase: Icons.Briefcase,
  wallet: Icons.Wallet,
  store: Icons.Store,
  hammer: Icons.Hammer,
  "circle-plus": Icons.CirclePlus,
  dumbbell: Icons.Dumbbell,
  "book-open": Icons.BookOpen,
  "glass-water": Icons.GlassWater,
  "list-checks": Icons.ListChecks,
  car: Icons.Car,
  plane: Icons.Plane,
  gift: Icons.Gift,
  coffee: Icons.Coffee,
  music: Icons.Music,
  gamepad: Icons.Gamepad2,
  baby: Icons.Baby,
  dog: Icons.Dog,
  shirt: Icons.Shirt,
  smartphone: Icons.Smartphone,
  wifi: Icons.Wifi,
  fuel: Icons.Fuel,
  pill: Icons.Pill,
  "piggy-bank": Icons.PiggyBank,
  sparkles: Icons.Sparkles,
  moon: Icons.Moon,
  sun: Icons.Sun,
  bed: Icons.Bed,
  brain: Icons.Brain,
  pen: Icons.PenLine,
  languages: Icons.Languages,
  bike: Icons.Bike,
  apple: Icons.Apple,
  droplet: Icons.Droplet,
  leaf: Icons.Leaf,
  heart: Icons.Heart,
  star: Icons.Star,
  target: Icons.Target,
  "trending-up": Icons.TrendingUp,
  receipt: Icons.Receipt,
  "credit-card": Icons.CreditCard,
  banknote: Icons.Banknote,
  building: Icons.Building2,
  palette: Icons.Palette,
  camera: Icons.Camera,
  code: Icons.Code,
  megaphone: Icons.Megaphone,
  users: Icons.Users,
  flame: Icons.Flame,
  mountain: Icons.Mountain,
  rocket: Icons.Rocket,
  clapperboard: Icons.Clapperboard,
  video: Icons.Video,
  film: Icons.Film,
  laptop: Icons.Laptop,
  monitor: Icons.Monitor,
  brush: Icons.Brush,
  image: Icons.Image,
  files: Icons.Files,
  "file-text": Icons.FileText,
  folder: Icons.Folder,
  globe: Icons.Globe,
  send: Icons.Send,
  mic: Icons.Mic,
  scissors: Icons.Scissors,
  lightbulb: Icons.Lightbulb,
  wrench: Icons.Wrench,
  "shopping-cart": Icons.ShoppingCart,
};

export const ICON_CHOICES = Object.keys(ICONS);

export function DynamicIcon({ name, className }: { name: string | undefined; className?: string }) {
  const Icon = (name && ICONS[name]) || Icons.Circle;
  return <Icon className={className} aria-hidden />;
}

export function IconBadge({ icon, color, className, size = "md" }: { icon: string; color: string; className?: string; size?: "sm" | "md" | "lg" }) {
  return (
    <span
      style={toneStyle(color)}
      className={cn(
        "inline-flex shrink-0 items-center justify-center rounded-lg tone-soft",
        size === "sm" && "size-7 [&_svg]:size-3.5",
        size === "md" && "size-9 [&_svg]:size-4",
        size === "lg" && "size-11 rounded-xl [&_svg]:size-5",
        className,
      )}
    >
      <DynamicIcon name={icon} />
    </span>
  );
}

// ── Money ────────────────────────────────────────────────────────────────────

export function Money({
  amount,
  className,
  tone,
  signed,
  compact,
}: {
  amount: Minor;
  className?: string;
  /** "auto" colours by sign; "income"/"expense" force a colour. */
  tone?: "auto" | "income" | "expense" | "muted";
  signed?: boolean;
  compact?: boolean;
}) {
  const fmt = useMoney();
  const color =
    tone === "income"
      ? "text-income"
      : tone === "expense"
        ? "text-expense"
        : tone === "muted"
          ? "text-muted-foreground"
          : tone === "auto"
            ? amount < 0
              ? "text-expense"
              : amount > 0
                ? "text-income"
                : ""
            : "";
  return <span className={cn("tabular whitespace-nowrap", color, className)}>{fmt(amount, { signed, compact })}</span>;
}

// ── Layout pieces ────────────────────────────────────────────────────────────

export function PageHeader({
  title,
  description,
  actions,
  className,
}: {
  title: React.ReactNode;
  description?: React.ReactNode;
  actions?: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={cn("flex flex-wrap items-end justify-between gap-x-4 gap-y-3", className)}>
      <div className="min-w-0">
        <h1 className="text-[22px] leading-tight font-semibold tracking-tight sm:text-2xl">{title}</h1>
        {description && <p className="mt-1 text-[13px] text-muted-foreground">{description}</p>}
      </div>
      {actions && <div className="flex flex-wrap items-center gap-2">{actions}</div>}
    </div>
  );
}

export interface SubNavItem {
  href: string;
  label: string;
  exact?: boolean;
}

export function SectionTabs({ items }: { items: SubNavItem[] }) {
  const pathname = usePathname();
  const norm = (p: string) => p.replace(/\/$/, "");
  const ref = React.useRef<HTMLDivElement>(null);
  React.useEffect(() => {
    ref.current?.querySelector<HTMLElement>("[aria-current=page]")?.scrollIntoView({ block: "nearest", inline: "center" });
  }, [pathname]);
  return (
    <nav aria-label="Secciones" className="-mx-4 sm:mx-0">
      <div ref={ref} className="no-scrollbar flex gap-1 overflow-x-auto px-4 sm:px-0">
        {items.map((item) => {
          const active = item.exact ? norm(pathname) === norm(item.href) : norm(pathname).startsWith(norm(item.href));
          return (
            <Link
              key={item.href}
              href={item.href}
              aria-current={active ? "page" : undefined}
              className={cn(
                "relative inline-flex h-9 shrink-0 items-center rounded-lg px-3 text-[13px] font-medium whitespace-nowrap text-muted-foreground transition-colors hover:bg-accent hover:text-foreground",
                active && "bg-card text-foreground shadow-[0_0_0_1px_var(--border)] hover:bg-card",
              )}
            >
              {item.label}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}

export function Card({ className, ...props }: React.ComponentProps<"section">) {
  return <section className={cn("rounded-xl border border-border bg-card shadow-[var(--shadow-card)]", className)} {...props} />;
}

export function CardHeader({
  title,
  description,
  action,
  className,
  icon,
}: {
  title: React.ReactNode;
  description?: React.ReactNode;
  action?: React.ReactNode;
  className?: string;
  icon?: React.ReactNode;
}) {
  return (
    <header className={cn("flex items-start justify-between gap-3 px-4 pt-4 pb-2 sm:px-5", className)}>
      <div className="flex min-w-0 items-start gap-2.5">
        {icon && <span className="mt-0.5 text-muted-foreground [&_svg]:size-4">{icon}</span>}
        <div className="min-w-0">
          <h2 className="text-[15px] leading-snug font-semibold">{title}</h2>
          {description && <p className="mt-0.5 text-xs text-muted-foreground">{description}</p>}
        </div>
      </div>
      {action && <div className="-mt-1 -mr-1.5 flex shrink-0 items-center gap-1">{action}</div>}
    </header>
  );
}

export function MetricCard({
  label,
  value,
  hint,
  tone,
  href,
  onClick,
  icon,
  className,
  emphasis,
}: {
  label: string;
  value: React.ReactNode;
  hint?: React.ReactNode;
  tone?: "income" | "expense" | "warning" | "brand";
  href?: string;
  onClick?: () => void;
  icon?: React.ReactNode;
  className?: string;
  emphasis?: boolean;
}) {
  const body = (
    <>
      <div className="flex items-center justify-between gap-2">
        <span className="text-[13px] font-medium text-muted-foreground">{label}</span>
        {icon && (
          <span
            className={cn(
              "text-subtle [&_svg]:size-4",
              tone === "income" && "text-income",
              tone === "expense" && "text-expense",
              tone === "warning" && "text-warning",
              tone === "brand" && "text-brand",
            )}
          >
            {icon}
          </span>
        )}
      </div>
      <div className={cn("mt-1.5 tabular font-semibold tracking-tight", emphasis ? "text-[26px] leading-8" : "text-xl leading-7")}>{value}</div>
      {hint && <div className="mt-1 text-xs text-muted-foreground">{hint}</div>}
    </>
  );
  const cls = cn(
    "block min-w-0 rounded-xl border border-border bg-card p-4 text-left shadow-[var(--shadow-card)]",
    (href || onClick) && "press transition-colors hover:border-border-strong hover:bg-accent/40 focus-visible:outline-2 focus-visible:outline-ring",
    className,
  );
  if (href)
    return (
      <Link href={href} className={cls}>
        {body}
      </Link>
    );
  if (onClick)
    return (
      <button type="button" onClick={onClick} className={cn(cls, "w-full")}>
        {body}
      </button>
    );
  return <div className={cls}>{body}</div>;
}

export function EmptyState({
  icon,
  title,
  description,
  action,
  className,
  compact,
}: {
  icon?: React.ReactNode;
  title: string;
  description?: React.ReactNode;
  action?: React.ReactNode;
  className?: string;
  compact?: boolean;
}) {
  return (
    <div className={cn("flex flex-col items-center justify-center text-center", compact ? "px-4 py-6" : "px-6 py-10", className)}>
      {icon && (
        <div className="mb-3 flex size-11 items-center justify-center rounded-xl border border-dashed border-border-strong text-muted-foreground [&_svg]:size-5">
          {icon}
        </div>
      )}
      <p className="text-sm font-medium">{title}</p>
      {description && <p className="mt-1 max-w-[42ch] text-[13px] text-muted-foreground">{description}</p>}
      {action && <div className="mt-4 flex flex-wrap justify-center gap-2">{action}</div>}
    </div>
  );
}

export function PageSkeleton() {
  return (
    <div className="space-y-5" aria-busy="true" aria-label="Cargando">
      <Skeleton className="h-8 w-48" />
      <div className="flex gap-2">
        {[0, 1, 2, 3].map((i) => (
          <Skeleton key={i} className="h-8 w-24" />
        ))}
      </div>
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        {[0, 1, 2, 3].map((i) => (
          <Skeleton key={i} className="h-24" />
        ))}
      </div>
      <div className="grid gap-4 lg:grid-cols-3">
        <Skeleton className="h-72 lg:col-span-2" />
        <Skeleton className="h-72" />
      </div>
    </div>
  );
}

export function SectionTitle({ children, action, className }: { children: React.ReactNode; action?: React.ReactNode; className?: string }) {
  return (
    <div className={cn("mb-2 flex items-center justify-between gap-2", className)}>
      <h3 className="text-[13px] font-semibold text-muted-foreground">{children}</h3>
      {action}
    </div>
  );
}

export function ListRow({
  className,
  onClick,
  children,
  as = "div",
}: {
  className?: string;
  onClick?: () => void;
  children: React.ReactNode;
  as?: "div" | "li";
}) {
  const Comp = as;
  if (onClick) {
    return (
      <Comp className={cn("list-none", className)}>
        <button
          type="button"
          onClick={onClick}
          className="flex w-full min-w-0 items-center gap-3 rounded-lg px-2 py-2.5 text-left transition-colors outline-none hover:bg-accent focus-visible:ring-2 focus-visible:ring-ring"
        >
          {children}
        </button>
      </Comp>
    );
  }
  return <Comp className={cn("flex min-w-0 items-center gap-3 px-2 py-2.5", className)}>{children}</Comp>;
}
