import { SiteShell } from "@jcc/core/components/SiteShell";
import { About } from "@jcc/core/sections/About";
import { Chapters } from "@jcc/core/sections/Chapters";
import { Contact } from "@jcc/core/sections/Contact";
import { Hero } from "@jcc/core/sections/Hero";
import { Impact } from "@jcc/core/sections/Impact";
import { MotionShowcase } from "@jcc/core/sections/MotionShowcase";
import { Process } from "@jcc/core/sections/Process";
import { Skills } from "@jcc/core/sections/Skills";
import { Toolkit } from "@jcc/core/sections/Toolkit";
import { chapters, content, copy, links, motionChapter, otherSite, workChapters } from "./site";

export default function Home() {
  return (
    <SiteShell links={links} role={copy.role}>
      <Hero hero={content.hero} />
      <MotionShowcase
        chapter={motionChapter}
        heading={[
          <span key="a">
            Made to <span className="em text-signal">Move.</span>
          </span>,
        ]}
        intro="Motion graphics hechos en After Effects y Premiere Pro: tipografía cinética, recortes, transiciones y ritmo. Cada pieza se reproduce en su formato original."
      />
      <Chapters
        chapters={workChapters}
        leading={[{ href: "#motion", number: motionChapter.number, title: motionChapter.title }]}
        intro="Explora cada proyecto a través de sus videos. Selecciona cualquiera para verlo en pantalla completa; al reproducirlo, el sonido se activa."
      />
      <About copy={copy} />
      <Skills groups={content.skills} />
      <Toolkit groups={content.toolkit} />
      <Impact chapters={chapters} />
      <Process steps={content.process} />
      <Contact links={links} otherSite={otherSite} role={copy.role} />
    </SiteShell>
  );
}
