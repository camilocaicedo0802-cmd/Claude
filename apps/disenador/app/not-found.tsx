import Link from "next/link";

export default function NotFound() {
  return (
    <main className="shell flex min-h-svh flex-col items-start justify-center gap-6">
      <p className="text-sm font-semibold text-signal">404</p>
      <h1 className="title max-w-[14ch]">
        Esta escena no quedó en el <span className="em text-signal">corte final.</span>
      </h1>
      <Link href="/" className="press inline-flex h-12 items-center bg-signal px-6 text-[0.8125rem] font-medium uppercase tracking-[0.06em]">
        Volver al inicio
      </Link>
    </main>
  );
}
