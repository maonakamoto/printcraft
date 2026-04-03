# PrintCraft

Custom artwork for physical surfaces — shower walls, canvases, tile murals. AI-generated scenes with recognizable faces, composed to exact print dimensions.

## How It Works

1. **Brief** — Client wants artwork on a physical surface. Define dimensions, scene, characters.
2. **Generate** — Create styled illustrations of each character/vehicle using AI (Grok, Midjourney, Flux)
3. **Composite** — Assemble individual elements into a unified scene at print resolution
4. **Deliver** — Export print-ready file, send to print shop

## Structure

```
printcraft/
├── app/                    # Next.js web app (composition editor)
├── projects/               # Client projects
│   └── duschwand-roli/     # Each project is self-contained
│       ├── BRIEF.md        # Client requirements, dimensions, scene description
│       ├── 00-source-photos/   # Real photos of people/vehicles
│       ├── 01-reference-art/   # Style references, previous attempts
│       ├── 02-grok-v1-*/       # Generation rounds (numbered by attempt)
│       ├── ...
│       ├── 05-composites/      # Assembled scenes
│       └── final/              # Print-ready exports
├── scripts/                # Reusable automation (Grok generation, compositing)
├── docs/                   # Process docs, learnings (carry forward between projects)
└── templates/              # Project templates for new clients
```

## Starting a New Project

1. Copy `templates/project/` to `projects/<name>/`
2. Fill in `BRIEF.md` — dimensions, scene, characters, style
3. Add source photos to `00-source-photos/`
4. Generate, iterate, composite, deliver

## Active Projects

### Duschwand Roli
Cartoon mural for shower wall on houseboat (River Queen K 2070).
- **Surface:** 2-panel L-corner glass (80 + 120 cm × 200 cm)
- **Scene:** 7 Amphicar 770 owners cruising Lake Garda at golden sunset
- **Style:** Retro 1960s travel poster / cartoon illustration
- **Status:** 4 style rounds complete (v1 initial → v4 retro poster). Compositing next.
- **Details:** [projects/duschwand-roli/BRIEF.md](projects/duschwand-roli/BRIEF.md)

## AI Tools for Face-Preserving Generation

| Tool | Face Likeness | Quality | Cost | Notes |
|------|--------------|---------|------|-------|
| Grok (xAI Aurora) | Good | Good | Free | Best free option. Browser automation needed. |
| Midjourney --cref | Good | Excellent | $10/mo | Character reference feature |
| Flux Pro + face swap | Very good | Excellent | ~$0.05/img | Via Replicate API |
| DALL-E | Poor | Good scenes | $0.04/img | EU filters block face likeness |

## Key Learnings

See [docs/PROCESS.md](docs/PROCESS.md) for detailed notes. Headlines:
- ChatGPT/DALL-E won't reproduce real faces (EU safety filters)
- Grok is best free option for face likeness but requires browser automation
- Grok's chat input (ProseMirror) sends on Enter — use Shift+Enter or clipboard paste for multi-line prompts
- Print minimum: 150 DPI at viewing distance. Target 200+ DPI when possible.
- Always generate with black/transparent background for easy compositing

## Tech Stack

- **App:** Next.js 16 + TypeScript + Tailwind + Konva.js
- **Scripts:** Python + Playwright (browser automation for Grok)
- **Compositing:** Python (Pillow) / GIMP scripts
- **Deploy:** Vercel
