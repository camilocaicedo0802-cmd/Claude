import { SiteShell } from "@jcc/core/components/SiteShell";
import { About } from "@jcc/core/sections/About";
import { Chapters } from "@jcc/core/sections/Chapters";
import { Contact } from "@jcc/core/sections/Contact";
import { Hero } from "@jcc/core/sections/Hero";
import { Impact } from "@jcc/core/sections/Impact";
import { LandingShowcase } from "@jcc/core/sections/LandingShowcase";
import { MotionShowcase } from "@jcc/core/sections/MotionShowcase";
import { Process } from "@jcc/core/sections/Process";
import { Skills } from "@jcc/core/sections/Skills";
import { Toolkit } from "@jcc/core/sections/Toolkit";
import { landings } from "@jcc/core/content/landings";
import { chapters, content, copy, links, motionChapter, workChapters } from "./site";

export default function Home() {
  return (
    <SiteShell links={links} role={copy.role}>
      <Hero hero={content.hero} />
      <MotionShowcase
        chapter={motionChapter}
        heading={[
          <span key="a">Cuando el diseño</span>,
          <span key="b" className="em text-signal">
            cobra vida.
          </span>,
        ]}
        intro="Mis piezas de motion graphics, hechas en After Effects y Premiere Pro. Cuando una pieza necesita movimiento, la llevo a video."
      />
      <Chapters
        chapters={workChapters}
        leading={[{ href: "#motion", number: motionChapter.number, title: motionChapter.title }]}
        intro="Explora cada proyecto a través de sus videos y piezas. Selecciona cualquiera para verlo en pantalla completa; al reproducir un video, el sonido se activa."
      />
      <About copy={copy} />
      <Skills groups={content.skills} />
      <Toolkit groups={content.toolkit} />
      <Impact chapters={chapters} showCampaigns />
      <Process steps={content.process} />
      <LandingShowcase landings={landings} />
      <Contact links={links} role={copy.role} />
    </SiteShell>
  );
}
