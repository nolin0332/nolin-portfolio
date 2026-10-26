# Nolin Whitbeck — Portfolio

Immersive WebGL portfolio for **Nolin Whitbeck**, Senior Applied AI/ML Engineer. Includes an embedded JotForm conversational agent.

## Run (Windows)

**Easiest:** double-click **`start.bat`** in this folder.

Or in a terminal:

```bash
npm install
npm run dev
```

Open **http://127.0.0.1:5138/**

## Personalize

Edit `scripts/resume-profile.json`, then:

```bash
npm run sync-assets
npm run personalize
```

Regenerate branding assets after a name change:

```bash
npm run generate-logo
python scripts/generate-favicon.py
python scripts/generate-cover.py
npm run generate-trailer   # hero trailer videos
```
