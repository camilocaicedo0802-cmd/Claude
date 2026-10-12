import { ArrowLeft, ArrowRight } from "lucide-react";
import Link from "next/link";
import { Reveal } from "../components/Reveal";
import { RevealText } from "../components/RevealText";
import { formatDuration, pieceSrc, posterSrc, videoMeta, videoSources } from "../content/media";
import type { Project } from "../content/types";
import { pad2 } from "../lib/format";

interface Props {
  project: Project;
  index: number;
  total: number;
  prev: Project;
  next: Project;
}

function Block({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <Reveal className="grid gap-3 border-t border-line py-8 md:grid-cols-12 md:gap-6 md:py-10">
      <h2 className="text-sm font-semibold text-signal md:col-span-3">{title}</h2>
      <div className="text-lg leading-relaxed text-paper md:col-span-8 md:col-start-5">{children}</div>
    </Reveal>
  );
}

export function CaseStudy({ project, index, total, prev, next }: Props) {
  const cs = project.caseStudy ?? {};
  const video = project.media.kind === "video" ? project.media.video : null;
  const meta = video ? videoMeta(video) : null;

  return (
    <article className="pt-[var(--nav-h)]">
      <div className="shell pb-10 pt-10 md:pb-14 md:pt-16">
        <Link href="/#trabajos" className="inline-flex items-center gap-2 text-sm text-fog hover:text-paper">
          <ArrowLeft aria-hidden size={16} /> Todos los proyectos
        </Link>
        <p className="mt-10 flex flex-wrap items-baseline gap-x-4 gap-y-1 text-sm font-medium">
          <span className="text-signal tabular">
            {pad2(index + 1)} / {pad2(total)}
          </span>
          <span className="text-smoke">{project.categories.join(" / ")}</span>
        </p>
        <RevealText as="h1" immediate className="display mt-5 max-w-[16ch]" lines={[project.title]} />
        {(project.client || project.context) && (
          <p className="mt-5 text-lg text-fog">{[project.client, project.context].filter(Boolean).join(" · ")}</p>
        )}
      </div>

      <div className="shell">
        {video && meta ? (
          <Reveal variant="wipe" className="flex justify-center bg-panel py-6 md:py-10">
            <video
              className="max-h-[80svh] w-auto max-w-full bg-ink"
              style={{ aspectRatio: `${meta.width} / ${meta.height}` }}
              poster={posterSrc(video)}
              controls
              playsInline
              preload="metadata"
              aria-label={`Video del proyecto ${project.title}`}
            >
              {videoSources(video).map((s) => (
                <source key={s.type} src={s.src} type={s.type} />
              ))}
            </video>
          </Reveal>
        ) : project.media.kind === "images" ? (
          <div className="grid gap-4 md:grid-cols-2 md:gap-6">
            {project.media.images.map((im, i, arr) => {
              const wide = im.width / im.height > 1.3 || arr.length === 1;
              return (
                <Reveal key={im.file} variant="wipe" delay={(i % 2) * 0.06} className={`flex items-center justify-center bg-panel p-4 md:p-10 ${wide ? "md:col-span-2" : ""}`}>
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img src={pieceSrc(im.file)} alt={im.alt} width={im.width} height={im.height} loading={i < 2 ? "eager" : "lazy"} decoding="async" className="h-auto max-h-[82svh] w-auto max-w-full object-contain" />
                </Reveal>
              );
            })}
          </div>
        ) : null}
      </div>

      <div className="shell mt-16 md:mt-24">
        <Reveal className="grid gap-6 pb-10 md:grid-cols-12">
          <p className="text-xl leading-relaxed md:col-span-8 md:text-2xl">{project.description}</p>
          <dl className="grid grid-cols-2 gap-6 text-sm md:col-span-3 md:col-start-10 md:grid-cols-1">
            <div>
              <dt className="text-smoke">Mi rol</dt>
              <dd className="mt-1">{project.role}</dd>
            </div>
            {project.year && (
              <div>
                <dt className="text-smoke">Año</dt>
                <dd className="mt-1 tabular">{project.year}</dd>
              </div>
            )}
            {meta && (
              <div>
                <dt className="text-smoke">Formato</dt>
                <dd className="mt-1 tabular">
                  {meta.height > meta.width ? "Vertical 9:16" : "Horizontal 16:9"} · {formatDuration(meta.duration)}
                </dd>
              </div>
            )}
            {project.tools.length > 0 && (
              <div>
                <dt className="text-smoke">Herramientas</dt>
                <dd className="mt-1">{project.tools.join(", ")}</dd>
              </div>
            )}
          </dl>
        </Reveal>

        {cs.objective && <Block title="Objetivo">{cs.objective}</Block>}
        {cs.need && <Block title="Necesidad del cliente">{cs.need}</Block>}
        {cs.solution && <Block title="Solución creativa">{cs.solution}</Block>}
        {cs.process && cs.process.length > 0 && (
          <Block title={video ? "Proceso de edición" : "Proceso"}>
            <ol className="space-y-3">
              {cs.process.map((step, i) => (
                <li key={step} className="flex gap-4">
                  <span className="text-sm font-semibold text-signal tabular">{pad2(i + 1)}</span>
                  <span>{step}</span>
                </li>
              ))}
            </ol>
          </Block>
        )}
        {cs.resources && cs.resources.length > 0 && <Block title="Recursos utilizados">{cs.resources.join(", ")}</Block>}
        {cs.result && <Block title="Resultado final">{cs.result}</Block>}
        {project.metrics && project.metrics.length > 0 && (
          <Block title="Métricas verificadas">
            <ul className="grid gap-6 sm:grid-cols-2">
              {project.metrics.map((m) => (
                <li key={m.label}>
                  <p className="text-4xl font-bold tabular">{m.value.toLocaleString("es-CO")}</p>
                  <p className="text-fog">{m.label}</p>
                  <p className="text-sm text-smoke">{m.context}</p>
                </li>
              ))}
            </ul>
          </Block>
        )}
      </div>

      <nav aria-label="Más proyectos" className="shell mt-16 grid gap-px border-y border-line bg-line md:mt-24 md:grid-cols-2">
        {[
          { p: prev, label: "Anterior", icon: <ArrowLeft aria-hidden size={18} /> },
          { p: next, label: "Siguiente", icon: <ArrowRight aria-hidden size={18} /> },
        ].map(({ p, label, icon }) => (
          <Link key={label} href={`/trabajos/${p.slug}/`} className={`group flex items-center gap-5 bg-ink py-8 md:px-6 ${label === "Siguiente" ? "md:flex-row-reverse md:text-right" : ""}`}>
            <span className="w-16 shrink-0 overflow-hidden bg-panel">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={p.media.kind === "video" ? posterSrc(p.media.video) : pieceSrc(p.media.images[0].file)}
                alt=""
                loading="lazy"
                className="aspect-[9/16] w-full object-cover transition-transform duration-500 group-hover:scale-105"
              />
            </span>
            <span className="min-w-0">
              <span className="flex items-center gap-2 text-sm text-smoke md:inline-flex">
                {icon} {label}
              </span>
              <span className="mt-1 block truncate text-xl font-semibold tracking-[-0.02em] group-hover:text-signal md:text-2xl">{p.title}</span>
            </span>
          </Link>
        ))}
      </nav>

    </article>
  );
}
