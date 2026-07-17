# Grok v4 — Retro Travel Poster (Apr 1)

## Approach
Single prompt per scene. Upload only the source photo (no style ref image — it caused color bleed in v2).
Style: 1960s Italian riviera travel poster. Pushing harder on consistency cues.

## Prompt Template

```
Transform this photo into a 1960s Italian travel poster illustration.

STYLE — follow this EXACTLY for every image in the series:
- Flat bold colors with subtle gradients, like vintage screen-printed posters
- Strong black ink outlines on all subjects (people, vehicles, water edges)
- Warm golden-hour palette: amber, coral, burnt orange sky — Lake Garda at sunset
- Simplified but recognizable backgrounds: silhouette hills, cypress trees, terracotta rooftops
- Water rendered as stylized horizontal bands of warm reflected color with white spray/wake
- Overall mood: nostalgic, warm, glamorous — like a 1962 Italian tourism advertisement

PEOPLE — highest priority:
- Faces must be RECOGNIZABLE as the real people in the photo
- Keep exact facial features, expressions, hair color/style, clothing, hats, sunglasses, accessories
- Render faces with more detail than the rest — semi-realistic within the poster style

VEHICLE — second priority:
- This is an Amphicar 770 (or other vehicle as shown). Keep it EXACTLY as photographed
- Preserve: body color, license plate text, chrome details, stripes, flags, tail fins, windshield shape
- Render with glossy poster-style shading and chrome highlights

COMPOSITION:
- Keep the same pose, angle, and framing as the original photo
- BLACK BACKGROUND above the waterline/horizon — this will be composited later
- No text, no titles, no watermarks
- Leave generous space around the subject on all sides
```

## Per-scene notes
All 7 use the same prompt above. The photo itself provides the vehicle/person specifics.
- Bild 1: Teal Amphicar B-AP 670, 3 people (Roli + gf + friend) — HERO image
- Bild 2: White Amphicar, Italian flag, stripy pants couple
- Bild 3: Teal Amphicar K-D, two guys in white tees
- Bild 4: Light blue Amphicar AB-N 274, Titanic-pose couple
- Bild 5: Hydrofoil boarder + dog (no car)
- Bild 6: Blue JETRANGER 66568, Dutch flag, man arms spread
- Bild 7: White amphibious VW van, woman on roof

## Generation method
Browser automation → grok.com, upload source photo, paste prompt, download result.
