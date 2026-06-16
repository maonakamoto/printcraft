# printcraft

Next.js application, self-hosted on Hetzner (bitbaum, behind Caddy) at
https://printcraft.orangecat.ch.

## Development

```bash
npm install
npm run dev        # http://localhost:3000
```

## Deployment

Self-hosted on the Hetzner box via the FleetCrown deploy tooling
(`scripts/hetzner/deploy.sh printcraft`): build → rsync standalone →
restart the systemd service → health-check. No Vercel.
