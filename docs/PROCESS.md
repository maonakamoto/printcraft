# PrintCraft Process Documentation

## Lesson 1: Face Likeness in AI Art (2026-03-25)

### Problem
ChatGPT/DALL-E generates cartoon scenes but with **generic faces** — EU-related safety filters prevent recognizable likenesses from reference photos.

### Solutions Tested / Known

| Tool | Face Likeness | Quality | Cost | Notes |
|------|--------------|---------|------|-------|
| ChatGPT/DALL-E | ❌ Generic | Good scenes | Free/Plus | Won't reproduce real faces |
| Grok (xAI Aurora) | ✅ Recognizable | Good | Free | Best free option for likenesses |
| Midjourney --cref | ✅ With reference | Excellent | $10/mo | Character reference feature |
| Flux Pro + face swap | ✅ Post-process | Very good | ~$0.05/img | Via Replicate API |
| ComfyUI + IP-Adapter | ✅ Full control | Excellent | Free (needs GPU) | Not viable without local hardware |

### Recommended Workflow (No Local GPU)
1. Generate base scene/composition (any tool)
2. Generate each character individually with face reference (Grok or Midjourney)
3. Composite characters into scene (Photopea/Canva)
4. Upscale final composite to print resolution
5. Color-correct for print (sRGB → print profile if needed)

## Lesson 2: Large Format Print Specs

- **Minimum DPI:** 150 for viewing distance >50 cm (shower wall = arm's length)
- **Preferred DPI:** 200–300 if achievable
- **Format:** PNG or TIFF, RGB (most large-format printers handle RGB→CMYK)
- **Bleed:** Add 2–5 mm per edge for cutting tolerance
- **Corner wraps:** Design must be continuous across seam — avoid faces/text at fold line
