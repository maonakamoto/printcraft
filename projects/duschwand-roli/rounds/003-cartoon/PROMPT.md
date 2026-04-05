# Grok v3 — Retro Cartoon Style (Mar 31)

## Approach
Shifted from gouache to bold retro cartoon. Only the original photo uploaded (no style reference image).
Automated via browser control script (`grok_gen_v4.py`).

## Prompt Template

```
Turn this photo into a retro cartoon illustration with a BLACK BACKGROUND.

This is part of a series of 7 images. Later I will combine them all into one panoramic scene (197cm × 190cm) printed on a two-panel glass shower wall. Each image will be placed at a specific position. So: frame the car and people as a complete unit with space around them on a black background, for easy compositing.

Style: Vintage 1960s travel poster meets European comic book. Rich painterly colors, warm golden tones, bold black outlines, slightly textured like a classic print. Think retro Amphicar advertisement art from the 1960s. This exact style must be consistent across all 7 illustrations.

FACES (highest priority): Must be EXACTLY recognizable as the real people. Same facial features, same expression, same hair, same clothing, same hats, same sunglasses. Do not simplify the faces.

CAR (second priority): This is an Amphicar 770. Keep EVERY detail exactly as in the photo — same color, same license plate, same stripes, same chrome bumpers, same tail fins, same windshield, same flags, same text on body. The Amphicar 770 has a very specific distinctive shape — keep it accurate.

Same pose, same angle as the photo. Show water around the car with spray and reflections. Everything above the water/horizon = solid black. No text, no watermarks.
```

## Results
- Best style consistency across all scenes (8-9/10 retro cartoon feel)
- Scene 1 (hero) failed on first batch run, succeeded on retry
- All 6 scenes generated successfully at 864-1536px
- Individual images look great
- **Composite still failed** — cartoon foregrounds on photographic background = collage effect
- Conclusion: need cartoon-style background OR single unified generation
