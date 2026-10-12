# Design

Fase 2 · Concepto visual. Shared by both sites (`apps/editor`, `apps/disenador`).

## Direction: "Corte final"

The world is the editing suite at the moment of the final cut: a black room, white type on the monitor, one red playhead. The page behaves like a timeline. Sections enter like cuts (a black mask opens on the next shot), headings print line by line like titles over picture, and the only red on screen is what an editor's eye would track: the playhead, the cut, the record light, the button that starts the job.

Mode: **Experience**. The work leads from the first viewport; the interface recedes into black around it.

Physical scene: a client opens the link on a phone in a meeting or at night, often in a dark room; a black interface frames vertical videos the way their own feed does, and keeps the colours of the work honest.

## Colour

Strategy: restrained, pinned by the brief (about 70 % black, 20 % white, 10 % red).

| Token | Value | Use |
| --- | --- | --- |
| `--ink` | `#080808` | page ground, video letterboxing |
| `--panel` | `#181818` | cards, panels, filter chips |
| `--panel-2` | `#202020` | hover/raised panel, input fields |
| `--line` | `#2a2a2a` | hairlines, dividers |
| `--paper` | `#ffffff` | headlines, key text |
| `--fog` | `#a3a3a3` | secondary text (7.9:1 on ink) |
| `--smoke` | `#7a7a7a` | captions, tertiary (4.6:1 on ink) |
| `--signal` | `#e50914` | playhead, CTA, keywords, numbering, active states |
| `--signal-deep` | `#a80f19` | hover/pressed of red elements |

Red never carries body text on black (contrast 4.1:1). It is used for large type, fills with white text (`#fff` on `#e50914` = 4.6:1), lines and indicators. No glow, no gradients on type, no other hue anywhere in the UI. Project media keeps its own colours.

Browser surfaces are themed: `::selection` red on white, red caret, dark scrollbar with a red thumb on hover, red focus ring with 3 px offset.

## Type

| Role | Face | Setting |
| --- | --- | --- |
| Display | Poppins 700 | `clamp(2.6rem, 6.4vw, 6rem)`, leading 0.98, tracking -0.035em |
| Display emphasis | Playfair Display Italic 500 | same size, leading 1.1 (descender clearance), tracking -0.01em, often red |
| Section title | Poppins 700 | `clamp(2.2rem, 5vw, 4.5rem)` |
| Body | Poppins 400 | 1rem / 1.7, max 62ch, `--fog` |
| UI label | Poppins 500 | 0.8125rem, tracking 0.04em, uppercase only on buttons |
| Numerals | Poppins 600 tabular | counters, project numbers |

Pairing pinned by the brief: a white sans headline with one word in red Playfair italic ("Selected *Works.*", "Behind the *Frames.*"). One emphasised word per heading, never more.

## Shape and depth

All-sharp system: radius 0 on media frames, cards and chips; buttons are 0-radius rectangles. The only round shapes are icon buttons on video controls (full circle) and the playhead dot. Depth comes from black-on-black layering (`--ink` / `--panel`) and from video, never from drop shadows.

## Layout

- 12-column grid, `max-width: 1440px`, gutters 24 px (16 px on phones).
- Hero: headline left (cols 1-7), 9:16 video right (cols 8-12) at up to 82 vh; on phones the video comes first, centered, capped at 50 svh tall so the headline and buttons fit on the first screen, text centered under it.
- Selected Works: one numbered chapter per Drive folder, in folder order. Each chapter is a header (number, title, context, description, link to the full page) plus a horizontal reel of its videos and pieces at a shared height (300 px phones, 380 px tablet, 440 px desktop); a sticky chip index jumps between chapters. Tapping any card opens the full-screen viewer (video with sound or the piece at 1600 px), with arrows, keyboard and swipe.
- Motion section: asymmetric editorial grid. The strongest piece takes a double-height 9:16 tile; 16:9 work spans wide; vertical pieces keep 9:16 (no cropping).
- Selected Works: filter bar + varied grid (alternating spans), case-study pages at `/trabajos/[slug]`.
- Sections alternate layout families: split hero, asymmetric grid, catalog grid, portrait split, stacked expanding rows (skills), typographic wall (toolkit), number field (impact), sticky timeline (process), full-bleed CTA (contact).

## Motion

Personality: precise, cinematic, never bouncy.

| Moment | Spec |
| --- | --- |
| Hero entrance | black mask lifts off the video (`clip-path: inset(100% 0 0 0)` to `inset(0)`, 900 ms, `--ease-cut`), headline lines rise from a mask with 70 ms stagger |
| Section heading | line-by-line reveal from `translateY(105%)` inside an overflow mask, 700 ms `--ease-out` |
| Media reveal | `clip-path` wipe from bottom, 800 ms, once, when 15 % visible |
| Section separator | 1 px red line scales from `scaleX(0)` to 1 on enter, 900 ms |
| Scroll playhead | fixed red progress line (`useScroll` + `scaleY`/`scaleX`), no state re-render |
| Card hover | preview video fades in over poster (200 ms), frame scales 1.02, red index number slides in |
| Buttons | `scale(0.97)` on press 160 ms, magnetic offset max 6 px on pointer-fine devices |
| Counters | count up once on view, 1.4 s ease-out, tabular numerals |
| Modal player | opens from the card (shared `layoutId`), 320 ms `--ease-drawer`; exit 200 ms |

Curves: `--ease-out: cubic-bezier(0.23, 1, 0.32, 1)`, `--ease-in-out: cubic-bezier(0.77, 0, 0.175, 1)`, `--ease-cut: cubic-bezier(0.7, 0, 0.2, 1)`, `--ease-drawer: cubic-bezier(0.32, 0.72, 0, 1)`. No `ease-in` on UI. Hover effects are gated behind `(hover: hover) and (pointer: fine)`; touch devices get tap-to-play and visible titles. `prefers-reduced-motion`: masks and transforms become instant, opacity fades kept at 150 ms, autoplay previews off (posters only), Lenis disabled.

## Video system

- Every clip ships as `videos/<slug>.mp4` (H.264, ≤1280 px), `previews/<slug>.mp4` (6 s, muted, 640 px) and `posters/<slug>.webp`.
- Hero video: `promo_editor_motion.mp4` on both sites, autoplay muted loop playsInline, poster first, sound toggle, play/pause, red progress.
- Grid: posters by default, previews load and play only on hover/visible-in-center, one at a time (a shared controller pauses the previous one).
- Full playback in a modal / case page with native controls, original aspect ratio, `preload="none"` until opened.

## Navigation

Minimal top bar (68 px): wordmark left, four links, one red CTA. Active section underlined by the red playhead. Mobile: wordmark + menu button opening a full-screen black sheet with large links (staggered), plus a floating WhatsApp button bottom-right that hides while the contact section is in view.
