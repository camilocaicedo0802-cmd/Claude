"use client";
import { MessageCircle } from "lucide-react";
import { AnimatePresence, motion, useMotionValueEvent, useScroll } from "motion/react";
import { useEffect, useState } from "react";
import { whatsappUrl } from "../content/profile";

/** Mobile-only floating WhatsApp button. Hidden on the hero and while the contact section is visible. */
export function WhatsAppFloat() {
  const [pastHero, setPastHero] = useState(false);
  const [contactVisible, setContactVisible] = useState(false);
  const { scrollY } = useScroll();
  useMotionValueEvent(scrollY, "change", (v) => setPastHero(v > window.innerHeight * 0.7));

  useEffect(() => {
    const contact = document.getElementById("contacto");
    if (!contact) return;
    const io = new IntersectionObserver(([e]) => setContactVisible(e.isIntersecting), { threshold: 0.1 });
    io.observe(contact);
    return () => io.disconnect();
  }, []);

  const show = pastHero && !contactVisible;
  return (
    <AnimatePresence>
      {show && (
        <motion.a
          href={whatsappUrl()}
          target="_blank"
          rel="noopener noreferrer"
          aria-label="Escribir por WhatsApp"
          className="press fixed bottom-[max(16px,env(safe-area-inset-bottom))] right-4 z-40 grid size-14 place-items-center rounded-full bg-signal text-paper shadow-[0_8px_24px_rgba(0,0,0,0.5)] lg:hidden"
          initial={{ opacity: 0, scale: 0.9, y: 12 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: 12, transition: { duration: 0.15 } }}
          transition={{ duration: 0.25, ease: [0.23, 1, 0.32, 1] }}
        >
          <MessageCircle size={24} />
        </motion.a>
      )}
    </AnimatePresence>
  );
}
