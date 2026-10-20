# Skill `matcha-avatar-video` — Instrucciones de uso

Esta skill guarda la configuración de los videos con avatar que hicimos en **Higgsfield** para promocionar el **Té Matcha Grado Ceremonial de LO Laboratorios Outlet**. Con ella, Claude puede repetir la campaña o crear videos nuevos con el mismo estilo sin que tengas que explicarle todo otra vez.

## Qué incluye

```
matcha-avatar-video/
├── SKILL.md                         ← instrucciones que lee Claude
├── config.json                      ← modelos, parámetros e IDs de Higgsfield
├── INSTRUCCIONES-DE-USO.md          ← este archivo
├── reference/
│   ├── doctor-ugc.md                ← 6 escenas del doctor (fotograma + video con voz)
│   ├── broll-kling.md               ← 5 tomas de apoyo sin diálogo
│   └── creadora-storyboard.md       ← variante de la creadora en cocina (tableros de 8 tomas)
└── assets/
    ├── producto-te-matcha.jpg       ← foto de referencia de la lata
    ├── avatar-doctor.jpg            ← avatar del doctor
    └── avatar-creadora.jpg          ← avatar de la creadora
```

## Los tres formatos guardados

| Formato | Qué es | Modelos de Higgsfield |
|---|---|---|
| **A. Doctor que habla a cámara** | 6 clips de 8 s (~48 s en total): gancho → problema → producto → por qué → beneficio → llamado a la acción. Habla en español con acento colombiano. | Nano Banana 2.1 (fotograma) + Veo 3.1 Lite con audio |
| **B. Tomas de apoyo** | 5 planos de 5 s sin voz: oficinista cansada, producto, batido, vertido sobre leche y profesional con energía. | Nano Banana 2.1 + Kling 3.0 (std, sin sonido) |
| **C. Creadora en cocina** | Storyboards de 8 tomas (cada uno equivale a un clip de 15 s) con una creadora UGC preparando el matcha. | GPT Image 2 + Seedream 5 Pro (realismo) |

Todo es vertical 9:16, listo para Reels, TikTok y Shorts.

## Requisitos

1. **Conector de Higgsfield conectado** en Claude (claude.ai → Configuración → Conectores) con tu cuenta.
2. **Créditos en Higgsfield.** Cada imagen y cada video gasta créditos. Claude te dirá el costo y te pedirá confirmación antes de generar.
3. Los IDs de `config.json` apuntan a imágenes de **tu** cuenta de Higgsfield. Si usas otra cuenta, Claude subirá las imágenes de `assets/` automáticamente.

## Cómo instalarla

**En Claude (web o app de escritorio):**
1. Ve a **Configuración → Capacidades → Skills**.
2. Pulsa **Subir skill** y elige `matcha-avatar-video.zip`.
3. Verifica que quede activada.

**En Claude Code (terminal):**
- Solo para un proyecto: descomprime el zip dentro de `.claude/skills/` del proyecto.
- Para todos tus proyectos: descomprímelo en `~/.claude/skills/`.

```bash
unzip matcha-avatar-video.zip -d ~/.claude/skills/
```

En este repositorio ya quedó instalada en `.claude/skills/matcha-avatar-video/`.

## Cómo usarla

Claude carga la skill solo cuando le pides algo relacionado con el matcha. En Claude Code también puedes llamarla directo con `/matcha-avatar-video`.

**Ejemplos de pedidos:**

- *"Genera de nuevo el anuncio completo del doctor con el té matcha."*
- *"Haz 3 ganchos nuevos con el doctor para el matcha, probando ángulos distintos: dormir mal, ansiedad por el café y productividad."*
- *"Cambia el llamado a la acción del doctor por: 'Escríbenos por WhatsApp y te lo enviamos hoy'."*
- *"Dame 2 tomas de apoyo nuevas del matcha: una con hielo en la playa y otra en un gimnasio."*
- *"Sigue con la creadora en cocina: haz el tablero 3 y luego anima los tres tableros."*
- *"Hazme una versión de 15 segundos: gancho, producto y llamado a la acción."*

**Qué hace Claude con un pedido:**
1. Lee la configuración y elige el formato (doctor, tomas de apoyo o creadora).
2. Escribe los prompts siguiendo la plantilla y las reglas (lata fiel, mismo avatar, acento colombiano, sin texto en pantalla).
3. Te muestra el costo en créditos y espera tu confirmación.
4. Genera los fotogramas, después los videos, y te entrega los resultados en orden de montaje.

## Cómo personalizarla

- **Cambiar frases del guion:** edita la tabla en `SKILL.md` y los prompts en `reference/doctor-ugc.md`. Cada frase debe tener unas 20 palabras como máximo para caber en 8 s.
- **Cambiar el acento o el idioma:** reemplaza `Latin American Spanish with a warm, natural Colombian accent` en los prompts de video.
- **Cambiar el avatar:** genera un avatar nuevo con `soul_2`, reemplaza su ID en `config.json` y actualiza la descripción física en las reglas de `SKILL.md`.
- **Otro producto:** sube la foto nueva, cambia el ID de `producto` en `config.json` y la descripción de la etiqueta en las reglas.

Después de editar, vuelve a comprimir la carpeta y súbela de nuevo a Claude.

## Importante antes de publicar

- **Contenido generado con IA.** El doctor y la creadora son personas sintéticas. TikTok, Meta y YouTube piden marcar el contenido realista hecho con IA. Activa esa etiqueta al publicar.
- **Publicidad de alimentos y salud.** Un "médico" que recomienda un producto puede estar regulado. En Colombia, revisa las normas del **INVIMA** y de la **SIC** sobre publicidad de alimentos y respaldo de profesionales de la salud antes de pautar. La skill evita afirmaciones médicas ("cura", "previene"), pero la revisión final es tuya.
- **Música y subtítulos.** Los videos salen sin música ni texto a propósito. Agrégalos en tu editor (CapCut, Premiere, etc.) con música que tengas licenciada.
