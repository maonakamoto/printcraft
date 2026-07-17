# New Project Template

Copy this directory to `projects/<client-name>/` to start a new project.

## Structure

```
<client-name>/
├── project.yaml        # SSOT — edit this first
├── source/             # Immutable inputs
│   ├── photos/         # Client-provided photos (references)
│   ├── references/     # Style references, inspiration
│   └── docs/           # Briefs, concept docs, contracts
├── rounds/             # Generation iterations (one dir per round)
│   └── 00N-name/
│       ├── manifest.yaml   # Date, model, outcome, learnings
│       ├── prompts/        # <scene-id>.txt
│       ├── outputs/        # Generated images
│       └── notes.md        # Free-form notes from this round
├── selected/           # Curated best-of (symlinks into rounds/)
│   ├── scenes/         # Best individual scenes
│   └── murals/         # Best unified-composition attempts
├── composites/         # Work-in-progress composites
└── deliverables/       # Final print-ready files (per panel)
```

## Workflow

1. Fill in `project.yaml` — dimensions, characters, scenes, style.
2. Drop source photos into `source/photos/`.
3. Generate: `printcraft generate all-scenes .` (or `generate scene . <id>`).
4. Review outputs in `rounds/00N/outputs/`.
5. Iterate — create new rounds until the style is right.
6. Symlink the best versions into `selected/scenes/` and `selected/murals/`.
7. Upscale selected mural to print resolution → `deliverables/`.
8. Send `deliverables/*.tif` (or .png) to the print shop.
