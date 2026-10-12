import { SiteShell } from "@jcc/core/components/SiteShell";
import { About } from "@jcc/core/sections/About";
import { Contact } from "@jcc/core/sections/Contact";
import { FeaturedPieces, HeroPieces } from "@jcc/core/sections/FeaturedPieces";
import { Hero } from "@jcc/core/sections/Hero";
import { Impact } from "@jcc/core/sections/Impact";
import { MotionShowcase } from "@jcc/core/sections/MotionShowcase";
import { Process } from "@jcc/core/sections/Process";
import { SelectedWorks } from "@jcc/core/sections/SelectedWorks";
import { Skills } from "@jcc/core/sections/Skills";
import { Toolkit } from "@jcc/core/sections/Toolkit";
import { content, copy, featuredTiles, heroPieces, links, motionProjects, otherSite, projects } from "./site";

export default function Home() {
  return (
    <SiteShell links={links} role={copy.role}>
      <Hero hero={content.hero} aside={<HeroPieces pieces={heroPieces} />} />
      <FeaturedPieces
        tiles={featuredTiles}
        heading={[
          <span key="a">
            Design that <span className="em text-signal">Sells.</span>
          </span>,
        ]}
        intro="Campañas, carruseles e identidades para redes. Algunas piezas se generaron con inteligencia artificial bajo mi dirección de arte, y así se indica en cada proyecto."
      />
      <MotionShowcase
        projects={motionProjects}
        heading={[
          <span key="a">
            Made to <span className="em text-signal">Move.</span>
          </span>,
        ]}
        intro="Cuando una pieza necesita movimiento, la llevo a video: motion graphics en After Effects y Premiere Pro, en su formato original."
      />
      <SelectedWorks projects={projects} filters={content.filters} />
      <About copy={copy} />
      <Skills groups={content.skills} />
      <Toolkit groups={content.toolkit} />
      <Impact projects={projects} showCampaigns />
      <Process steps={content.process} />
      <Contact links={links} otherSite={otherSite} role={copy.role} />
    </SiteShell>
  );
}
