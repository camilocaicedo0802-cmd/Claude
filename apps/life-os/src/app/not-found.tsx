import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex flex-col items-center py-24 text-center">
      <p className="text-sm text-muted-foreground">Error 404</p>
      <h1 className="mt-2 text-xl font-semibold">Esta página no existe</h1>
      <Link href="/vida/" className="mt-5 text-sm font-medium text-brand underline-offset-4 hover:underline">
        Volver a Mi día
      </Link>
    </div>
  );
}
