# printcraft

Next.js application, self-hosted on Hetzner (bitbaum, behind Caddy) at
https://printcraft.orangecat.ch.

## Repository layout

**The application lives in `app/`, not at the repo root.**

| Path | What it is |
| --- | --- |
| `app/` | **The deployed Next.js app.** Its own `package.json`, `src/`, `supabase/`. This is what CI gates and what the box runs. |
| `printcraft/`, `projects/`, `templates/`, `pyproject.toml` | The Python image-generation / compositor pipeline (see `PIPELINE.md`). |
| root `src/`, `next.config.ts`, `package.json`, `tsconfig.json`, `eslint.config.mjs`, `postcss.config.mjs`, `components.json`, `package-lock.json` | **Stale duplicate.** A frozen copy of the Next app from 2026-03-28, unioned back into `main` by the unrelated-history merge `e657365` (2026-07-17). Nothing builds it, nothing deploys it, and it lacks the self-hosted Supabase migration (`db: { schema: 'printcraft' }`, `supabase.orangecat.ch`) and `output: "standalone"`. Do not develop against it — and do not mistake `app/` for the duplicate when cleaning up. |

The deploy registry is the source of truth for which directory ships:
`fleetcrown/scripts/hetzner/apps.conf` →
`printcraft|4015|printcraft.orangecat.ch|/home/g/dev/printcraft|app|-` (field 5 = `APP_DIR`).

## Development

```bash
cd app
npm install
npm run dev        # http://localhost:3000
npm run verify     # lint + typecheck — same command CI runs
```

## Deployment

Self-hosted on the Hetzner box via the FleetCrown deploy tooling
(`scripts/hetzner/deploy.sh printcraft`): build → rsync standalone →
restart the systemd service → health-check. No Vercel.
