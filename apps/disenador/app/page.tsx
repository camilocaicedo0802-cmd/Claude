import { SiteShell } from "@jcc/core/components/SiteShell";
import { About } from "@jcc/core/sections/About";
import { Chapters } from "@jcc/core/sections/Chapters";
import { Contact } from "@jcc/core/sections/Contact";
import { Hero } from "@jcc/core/sections/Hero";
import { HeroPieces } from "@jcc/core/sections/HeroPieces";
import { Impact } from "@jcc/core/sections/Impact";
import { MotionShowcase } from "@jcc/core/sections/MotionShowcase";
import { Process } from "@jcc/core/sections/Process";
import { Skills } from "@jcc/core/sections/Skills";
import { Toolkit } from "@jcc/core/sections/Toolkit";
import { chapters, content, copy, heroPieces, links, motionChapter, otherSite, workChapters } from "./site";

export default function Home() {
  return (
    <SiteShell links={links} role={copy.role}>
      <Hero hero={content.hero} aside={<HeroPieces pieces={heroPieces} />} />
      <MotionShowcase
        chapter={motionChapter}
        heading={[
          <span key="a">
            Made to <span className="em text-signal">Move.</span>
          </span>,
        ]}
        intro="Mis piezas de motion graphics, hechas en After Effects y Premiere Pro. Cuando una pieza necesita movimiento, la llevo a video."
      />
      <Chapters
        chapters={workChapters}
        leading={[{ href: "#motion", number: motionChapter.number, title: motionChapter.title }]}
        intro="Cada proyecto con sus piezas y videos, en orden de importancia. Toca cualquiera para verlo en grande; los videos suenan al abrirlos."
      />
      <About copy={copy} />
      <Skills groups={content.skills} />
      <Toolkit groups={content.toolkit} />
      <Impact chapters={chapters} showCampaigns />
      <Process steps={content.process} />
      <Contact links={links} otherSite={otherSite} role={copy.role} />
    </SiteShell>
  );
}
