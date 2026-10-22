# Flujo B — Tomas de apoyo con Kling 3.0: prompts completos

Fotograma: `nano_banana_2_1`, 9:16, `2k`, `thinking_level: "high"`. Cuando sale el frasco, va en `medias` el producto `59675887-7a35-45f3-9e99-b0e6393e8b9b` con `role: "image_references"`.
Video: `kling3_0`, 9:16, `duration: 5`, `mode: "std"`, `sound: "off"`, con el fotograma como `start_image`. Si Higgsfield responde recomendando un preset en lugar de generar, repite con `declined_preset_id` igual al ID que devuelve.

**Lo que hizo que el frasco saliera fiel:** dictar el texto exacto de la etiqueta (el bloque "Texto del frasco" de abajo) y poner el frasco grande y enfocado. Si solo se pide "the exact canister", el modelo inventa la letra pequeña (salió "50" porciones en vez de 30). Revisa siempre la franja verde de abajo antes de animar.

## Texto del frasco (pegar en todo prompt donde aparezca)

```
the EXACT matcha canister from the reference image, reproduced pixel-faithfully like a photo of the same physical object: same cylindrical paper canister with thin metallic rim, same cream label and layout. Label text must be spelled exactly: 'fytosofy' / 'Nutrition' under the green leaf emblem; tab 'ORIGEN' 'JAPÓN' '日本産' with torii icon and Japanese flag; 'TÉ' 'MATCHA'; 'GRADO CEREMONIAL PREMIUM'; '100% PURO EN POLVO'; 'IMPORTADO DIRECTAMENTE DESDE JAPÓN'; round seal 'GRADO CEREMONIAL PREMIUM'; bottom band icon captions '100G TÉ VERDE MATCHA PURO', 'GRADO CEREMONIAL PREMIUM', 'CERTIFICADO DE ORIGEN JAPÓN', 'SIN AZÚCARES AÑADIDOS', 'SIN ADITIVOS SIN CONSERVANTES'; bottom line 'TÉ VERDE EN POLVO', 'Contenido Neto 60g', 'Porciones 30 (2 g por porción)'. Do not redesign, re-letter, recolor, simplify or rearrange anything; same front angle as the reference, label facing the camera.
```

En los prompts de abajo, `<TEXTO DEL FRASCO>` es ese bloque.

## Toma 1 — Oficinista cansada (problema)

No sale el frasco, así que no cambia.

**Fotograma** — sin medias. Job: `917f01a9-b216-438e-92fa-23a8595281e6`
```
Hyperrealistic vertical UGC smartphone photo. A tired Latin American office worker woman around 30, dark hair in a messy bun, beige blazer, slumped at her office desk in the afternoon, rubbing her eyes with one hand, visibly exhausted. On the desk: three empty paper coffee cups lined up, a laptop with spreadsheets, sticky notes. Modern open-plan office, warm late-afternoon window light, slightly desaturated tired mood, real skin texture, candid side angle. No text, no logos.
```

**Video** — Job: `aeaef50b-c81e-46cc-9802-6af326140efa`
```
Realistic handheld smartphone footage. The exhausted office worker rubs her eyes, sighs and lets her head drop slightly, then pushes an empty coffee cup aside with a frustrated look. Subtle slow push-in camera. Natural office ambience mood, warm afternoon light. Keep the scene and the person consistent, no text.
```

## Toma 2 — Hero de producto

**Fotograma** — Job: `22d672bd-c39d-4554-b93a-b97a7eae722d`
```
Hyperrealistic vertical premium product hero photo. The product is <TEXTO DEL FRASCO> The number of servings is 30, never 50. The canister stands large in the lower-middle of the frame on a white marble kitchen counter next to a small black ceramic bowl of vivid bright green matcha powder, a bamboo whisk, a bamboo scoop and a few fresh green tea leaves. Bright morning sunlight with soft leaf shadows, airy kitchen softly blurred behind, fresh vibrant high-end commercial look. Exactly one canister in frame. No extra text, no other brands.
```

**Video** — Job: `9cc21dfd-4ca2-4d07-b289-9088554ce05a`
```
Premium product commercial shot. Very slow, gentle camera push-in toward the matcha canister standing on the marble counter. The canister is a rigid object: it does not move, rotate, bend or deform, and its label stays exactly as in the first frame — same text, logo, colors and layout, sharp and unchanged in every frame. Sunlight and soft leaf shadows move slightly across the counter, a little matcha powder dust floats in the light beam. No text overlays.
```

## Toma 3 — Batido macro

**Fotograma** — Job: `14f1abf5-79ff-4bc8-9e37-1e437a81da29`
```
Hyperrealistic vertical macro food photo at a 45 degree angle: a bamboo whisk whisking vivid bright green matcha in a matte black ceramic bowl, creamy fine foam on top. Behind the bowl, in focus and clearly readable, stands <TEXTO DEL FRASCO> White marble counter, bright natural window light, vibrant fresh colors, premium commercial look. Exactly one canister in frame. No extra text, no other brands.
```

**Video** — Job: `6494fcf6-e3fe-42eb-9673-481e47796130`
```
Macro food commercial footage. The hand whisks the vivid green matcha quickly in a zigzag W motion with the bamboo whisk, creamy foam forms and swirls, tiny bubbles. Static camera. The matcha canister behind the bowl is a rigid object that stays completely still: it does not move, rotate or deform, and its label stays exactly as in the first frame — same text, logo, colors and layout in every frame. Bright natural light, slight slow motion feel. No text overlays.
```

## Toma 4 — Vertido sobre leche con hielo

**Fotograma** — Job: `42ab950e-19e9-48e9-829c-43377b7cb6cf`
```
Hyperrealistic vertical food commercial photo, side view at counter height: vivid bright green whisked matcha being poured from a small glass pitcher into a tall clear glass filled with ice cubes and white milk, beautiful green swirls blending into the milk. Right next to the glass, large in the frame and in sharp focus, stands <TEXTO DEL FRASCO> White marble counter, bright soft daylight, fresh appetizing premium look. Exactly one canister in frame. No extra text, no other brands.
```

**Video** — Job: `dbb18a60-0389-4bd9-b6be-62d2be498895`
```
Slow motion food commercial footage. Vivid green matcha pours from the glass pitcher into the tall glass of ice and milk, creating beautiful green swirls cascading down through the milk and around the ice cubes. Static camera with a very subtle push-in. The matcha canister next to the glass is a rigid object that stays completely still: it does not move, rotate or deform, and its label stays exactly as in the first frame — same text, logo, colors and layout in every frame. Bright daylight. No text overlays.
```

## Toma 5 — Profesional con energía (solución)

**Fotograma** — Job: `923eda45-5c14-4293-91cf-7ea1cf0ad041`
```
Hyperrealistic vertical UGC smartphone photo. A young Latin American professional woman around 28, long dark hair, light blue blouse, at a bright modern office desk, happily sipping an iced matcha latte (vivid green layered over milk with ice) through a straw, energized, focused and smiling, laptop open. Close to the camera in the lower foreground, the canister fills about one third of the frame height and is in sharp focus: <TEXTO DEL FRASCO> The tab says ORIGEN, never GREEN. Bright daylight, fresh positive mood, real skin texture, candid. Exactly one canister in frame. No extra text, no other brands.
```

**Video** — Job: `2e0f86fa-1dd2-443f-949f-5184ce4c7164`
```
Realistic handheld smartphone UGC footage, very steady. The young woman sips her iced matcha latte through the straw, lowers the glass, smiles with energy and goes back to typing on her laptop, focused and happy. The matcha canister in the foreground is a rigid object that stays completely still: it does not move, rotate or deform, and its label stays exactly as in the first frame — same text, logo, colors and layout in every frame. Bright office daylight. No text overlays.
```

## Dónde intercalarlas

- Toma 1 → después de la escena 2 del doctor (problema).
- Tomas 2, 3 y 4 → después de la escena 3 (revelación) o como fondo de la escena 4.
- Toma 5 → junto a la escena 5 (beneficio).
