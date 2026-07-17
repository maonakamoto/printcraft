# PrintCraft Learnings

Hard-won findings that took real time to discover. Read this before your next session.

---

## Grok browser automation

### The short-prompt rule (most important)
**Grok routes image+photo requests based on prompt length.**

- **Short prompts (< ~600 chars)** → Aurora image model → produces illustrations
- **Long prompts (> ~600 chars)** → Grok 4.20 text model → does photo *editing* (wrong!)

Even with a great prompt template that worked perfectly on round 005-retro-poster,
if you paste a 1,300-character version into SuperGrok you'll get a photorealistic
enhancement of the uploaded photo — not the retro illustration you asked for.

**Always compress your prompt.** If you find yourself writing paragraphs, you're about
to get the wrong model.

### Textarea interaction
Grok switched from ProseMirror to a standard `<textarea>` sometime in early 2026.
This is great — newlines work natively. But interaction rules still matter:

| Method | Works? | Why |
|---|---|---|
| `page.keyboard.type(prompt, delay=2)` | **YES** | Triggers React's onChange chain properly |
| `textarea.fill(prompt)` | Usually | But fails when textarea is "hidden" after file upload |
| `element.type(prompt)` | NO after upload | Times out — element not visible |
| JS native setter + `input` event | NO | Grok receives the prompt but routes to text mode (wrong output) |

**Always use `page.keyboard.type()`** after focusing the textarea via JS:

```python
page.evaluate("() => document.querySelector('textarea').focus()")
page.keyboard.type(prompt, delay=2)
```

### Submit button
The submit button (`aria-label="Absenden"` in German, `"Submit"` in English) becomes
**hidden** (not `display:none`, but not visible to Playwright) after a file is uploaded.
You can't click it via `page.click(selector)`.

**Click via JS:**
```python
page.evaluate("""() => {
    const btn = document.querySelector('button[aria-label="Absenden"]')
             || document.querySelector('button[aria-label="Submit"]');
    if (btn) btn.click();
}""")
```

### Image URL patterns
Generated images live at:
```
https://assets.grok.com/users/{uuid}/generated/{uuid}/...
https://assets.grok.com/anon-users/{uuid}/generated/{uuid}/...
```

The `/generated/` segment is the key. URLs without it are uploaded reference photos
(`.../content`). Always filter on `/generated/` or you'll "download" the input.

### Rate limits
- **Free tier:** ~3 image generations per 2 hours per IP/session
- **SuperGrok:** effectively unlimited for image generation when using short prompts
- Rate limit message (German): `"Limit wird alle 2 Stunden zurückgesetzt"`
- When rate limited, Grok responds with text instead of an image (no error message)

---

## Chrome / CDP / Browser extension

### NativeMessagingHosts per profile
The Claude browser extension uses Chrome Native Messaging. The config file lives at:
```
~/.config/google-chrome/NativeMessagingHosts/com.anthropic.claude_code_browser_extension.json
```

**If you launch Chrome with `--user-data-dir=/some/custom/path`,** Chrome only reads
`NativeMessagingHosts/` from that custom dir — NOT the default location.

Fix: copy the config into every custom profile you use:
```bash
cp ~/.config/google-chrome/NativeMessagingHosts/com.anthropic.claude_code_browser_extension.json \
   /your/custom/data/dir/NativeMessagingHosts/
```

### CDP requires non-default data dir
```
DevTools remote debugging requires a non-default data directory.
Specify this using --user-data-dir.
```

You cannot use `--remote-debugging-port=9222` with Chrome's default profile.
Create a separate profile dir (e.g. `~/.config/chrome-grok`) and use it for
automation work.

### Full CDP launch command
```bash
/opt/google/chrome/chrome \
  --user-data-dir=/home/g/.config/chrome-grok \
  --profile-directory=Default \
  --remote-debugging-port=9222 \
  --remote-allow-origins=* \
  "https://grok.com/"
```

The `--remote-allow-origins=*` is **required** — without it, Playwright can't
connect to the CDP websocket (403 Forbidden).

### Cloudflare blocks Playwright's own browser
Launching Chromium via `playwright.chromium.launch()` adds `--enable-automation`
(visible in the user agent and via navigator.webdriver). Cloudflare detects this
on x.ai login pages and blocks with "Sorry, you have been blocked."

**Workaround:** connect to an existing manually-launched Chrome via CDP. The user
data dir approach also lets the session persist across runs.

---

## Print specs

- **Minimum DPI:** 150 for arm's-length viewing (shower wall, canvas)
- **Preferred DPI:** 200-300 if achievable
- **Bleed:** 2-5 mm per edge for cutting tolerance
- **Corner wraps:** Never put faces or text across the fold line

### Duschwand Roli specifically
- Two panels: 80 × 200 cm (left) + 120 × 200 cm (right)
- At 150 DPI: 4,724 × 11,811 px (left) + 7,086 × 11,811 px (right)
- Total unwrapped: 200 × 200 cm → 11,811 × 11,811 px

---

## Compositing — the big lesson

**Do not composite individually generated scenes onto a shared background.**

Round 004 (2026-04-01) tried exactly this. The result looked like a collage:
- Scale mismatch between vehicles
- Jarring waterline seams where each scene's water met the background
- No shared perspective or lighting direction
- Photo background + cartoon foreground = broken

Instead, **generate the full scene as one image** (round 007). Give the AI the
entire mural layout in one prompt. It figures out the perspective, water, and
atmospheric consistency because it's drawing one picture.

Use the individually-generated scenes only as:
- Face-likeness references (upload the best one as a style anchor)
- QA material to verify the unified output matches what the client wants

---

## Prompt engineering for retro poster style

What works:
- "1960s Italian travel poster illustration"
- "Bold black ink outlines"
- "Flat cel-shaded colors"
- "Warm golden-hour palette: amber, coral, burnt orange"
- "Stylized water, horizontal color bands with white spray"
- "Nostalgic, glamorous, like a 1962 tourism advertisement"
- Explicit: "No text. No watermarks. No signatures."
- Explicit: "Portrait orientation" or "tall vertical composition" for non-landscape

What causes drift:
- Uploading a style-reference image alongside the photo (color bleed, round 002)
- Omitting "no text" (get random "LAGO DI GARDA" overlays, round 007 attempt 5)
- Saying "edit this photo" or "transform this photo into X" (triggers photo-edit mode)
- Very long prompts (triggers text-model routing, see short-prompt rule)

---

## File organization

### Prompts MUST be stored with outputs
Every round directory has `prompts/<scene-id>.txt` alongside `outputs/<scene-id>.jpg`.
Six months from now you'll need to know exactly what prompt produced that one good
image. Don't lose that mapping.

### Manifest per round
Every round needs a `manifest.yaml` with:
- Date, model, status, outcome
- Which outputs made it to `selected/`
- What was learned
- What the next step was

Without this, rounds become a graveyard of forgotten attempts.

### Selected/curated layer
Use `selected/scenes/` and `selected/murals/` with **symlinks** pointing into
`rounds/`. This gives you a clear "this is the one" view without duplicating files
and without losing the round context.

### Never delete source materials
`source/photos/`, `source/references/`, `source/docs/` are immutable. Copy them in,
never modify, never delete. Regeneration is cheap; losing originals is catastrophic.
