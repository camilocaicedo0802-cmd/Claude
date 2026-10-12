import { SiteShell } from "@jcc/core/components/SiteShell";
import { About } from "@jcc/core/sections/About";
import { Contact } from "@jcc/core/sections/Contact";
import { Hero } from "@jcc/core/sections/Hero";
import { Impact } from "@jcc/core/sections/Impact";
import { MotionShowcase } from "@jcc/core/sections/MotionShowcase";
import { Process } from "@jcc/core/sections/Process";
import { SelectedWorks } from "@jcc/core/sections/SelectedWorks";
import { Skills } from "@jcc/core/sections/Skills";
import { Toolkit } from "@jcc/core/sections/Toolkit";
import { content, copy, links, motionProjects, otherSite, projects } from "./site";

export default function Home() {
  return (
    <SiteShell links={links} role={copy.role}>
      <Hero hero={content.hero} />
      <MotionShowcase
        projects={motionProjects}
        heading={[
          <span key="a">
            Made to <span className="em text-signal">Move.</span>
          </span>,
        ]}
        intro="Motion graphics hechos en After Effects y Premiere Pro: tipografía cinética, recortes, transiciones y ritmo. Cada pieza se reproduce en su formato original."
      />
      <SelectedWorks projects={projects} filters={content.filters} />
      <About copy={copy} />
      <Skills groups={content.skills} />
      <Toolkit groups={content.toolkit} />
      <Impact projects={projects} />
      <Process steps={content.process} />
      <Contact links={links} otherSite={otherSite} role={copy.role} />
    </SiteShell>
  );
}
