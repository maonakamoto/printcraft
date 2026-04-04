#!/usr/bin/env python3
"""
Grok image generation v5 — for PrintCraft projects.

Uses Playwright to automate grok.com image generation.
Grok now uses a standard <textarea> — newlines work natively.

Usage:
  python3 grok_gen_v5.py test            # Dry run scene 0 (no submit)
  python3 grok_gen_v5.py 0               # Generate scene 0
  python3 grok_gen_v5.py 0 3             # Generate scenes 0-3
  python3 grok_gen_v5.py all             # Generate all scenes
"""

import sys
import time
import os
import base64
from pathlib import Path
from playwright.sync_api import sync_playwright

# --- Project paths ---
PROJECT = Path("/home/g/dev/printcraft/projects/duschwand-roli")
PHOTOS = PROJECT / "00-source-photos"
OUTPUT = PROJECT / "08-grok-v5-final"

# --- Style block (shared across all scenes for consistency) ---
STYLE = """Style: 1960s ITALIAN TRAVEL POSTER illustration.

STYLE RULES (follow EXACTLY for every image):
- Flat bold colors with subtle gradients, like vintage screen-printed posters
- Strong black ink outlines on all subjects (people, vehicles, water edges)
- Warm golden-hour palette: amber, coral, burnt orange sky — Lake Garda at sunset
- Water as stylized horizontal bands of warm reflected color with white spray/wake
- Overall mood: nostalgic, warm, glamorous — like a 1962 Italian tourism ad

PEOPLE (highest priority):
- Faces MUST be RECOGNIZABLE as the real people in the photo
- Keep exact facial features, expressions, hair color/style, clothing, hats, sunglasses
- Render faces with more detail than the rest — semi-realistic within the poster style

VEHICLE:
- Keep it EXACTLY as photographed: body color, license plate, chrome, stripes, flags
- Glossy poster-style shading with chrome highlights

COMPOSITION:
- Same pose, angle, framing as original photo
- BLACK BACKGROUND above waterline/horizon (for compositing)
- No text, no titles, no watermarks
- Generous space around subject on all sides"""

# --- Scene definitions ---
SCENES = [
    {
        "name": "bild1_hero_teal_bap670",
        "photo": "1.png",
        "extra": "TEAL/TURQUOISE Amphicar 770, license plate B-AP 670. THREE people aboard. Gold chrome stripes, tail fins. This is the HERO image — center of the mural.",
    },
    {
        "name": "bild2_white_italian",
        "photo": "2.png",
        "extra": "WHITE Amphicar 770 with red stripe accents and Italian flag. TWO people — one wears STRIPY PANTS (key detail, get this right!).",
    },
    {
        "name": "bild3_teal_kd",
        "photo": "3.png",
        "extra": "Another Amphicar on the water. Recreate people and vehicle exactly as shown.",
    },
    {
        "name": "bild4_blue_abn274",
        "photo": "4.png",
        "extra": "LIGHT BLUE/PASTEL BLUE Amphicar 770, license plate AB-N 274. TWO people in Titanic-like pose (arms spread).",
    },
    {
        "name": "bild5_hydrofoil_dog",
        "photo": "5.png",
        "extra": "Person on HYDROFOIL BOARD with GOLDEN RETRIEVER DOG. Dynamic water spray, foil above surface. Dog should be cute and cartoonish.",
    },
    {
        "name": "bild6_jetranger",
        "photo": "6.png",
        "extra": 'BLUE amphibious vehicle/truck with "66568 JETRANGER" text and DUTCH FLAG. Man with ARMS SPREAD WIDE, passengers aboard.',
    },
    {
        "name": "bild7_vw_van",
        "photo": "7.png",
        "extra": "WHITE amphibious VW-type van. WOMAN ON ROOF in chair, couple inside. Stylized wake and reflections.",
    },
]


def build_prompt(scene):
    return f"""Turn this photo into a retro cartoon illustration for a large-format print mural.

{STYLE}

SPECIFIC SCENE:
{scene['extra']}"""


def generate_scene(context, scene, dry_run=False):
    """Generate one scene. Returns True on success."""
    name = scene["name"]
    photo_path = str(PHOTOS / scene["photo"])
    prompt = build_prompt(scene)

    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")

    page = context.new_page()
    page.goto("https://grok.com/", wait_until="domcontentloaded", timeout=30000)
    # Wait for React app to render the textarea
    try:
        page.wait_for_selector("textarea", timeout=20000)
    except:
        time.sleep(10)  # extra fallback wait
    time.sleep(2)

    # 1. Upload photo
    file_input = page.query_selector('input[type="file"]')
    if not file_input:
        print("  ERROR: No file input found")
        page.screenshot(path=str(OUTPUT / f"debug_{name}_nofile.png"))
        page.close()
        return False

    if not os.path.exists(photo_path):
        print(f"  ERROR: Photo not found: {photo_path}")
        page.close()
        return False

    file_input.set_input_files(photo_path)
    time.sleep(3)
    print(f"  Photo uploaded")

    # 2. Enter prompt — textarea supports newlines natively
    #    After file upload, textarea may not be visible until we click the input area
    textarea = None
    for attempt in range(5):
        textarea = page.query_selector("textarea")
        if textarea and textarea.is_visible():
            break
        # Try clicking the placeholder / input area to activate it
        placeholder = page.query_selector('[placeholder]') or page.query_selector('[data-placeholder]')
        if placeholder:
            try:
                placeholder.click(timeout=3000)
            except:
                pass
        # Also try clicking in the general input area
        input_area = page.query_selector('div:has(> textarea)')
        if input_area:
            try:
                input_area.click(timeout=3000)
            except:
                pass
        time.sleep(2)
    if not textarea or not textarea.is_visible():
        # Last resort: use JS to make textarea visible and focus it
        page.evaluate("""() => {
            const ta = document.querySelector('textarea');
            if (ta) {
                ta.style.display = 'block';
                ta.style.visibility = 'visible';
                ta.focus();
            }
        }""")
        time.sleep(1)
        textarea = page.query_selector("textarea")
    if not textarea:
        print("  ERROR: No textarea found at all")
        page.screenshot(path=str(OUTPUT / f"debug_{name}_nota.png"))
        page.close()
        return False

    try:
        textarea.click(timeout=5000)
    except:
        textarea.focus()
    time.sleep(0.3)
    textarea.fill(prompt)
    time.sleep(0.5)

    # Verify
    value = textarea.input_value()
    if len(value.strip()) < 50:
        print(f"  WARNING: fill() got {len(value)} chars, retrying with JS...")
        page.evaluate("""(text) => {
            const ta = document.querySelector('textarea');
            const nativeSetter = Object.getOwnPropertyDescriptor(
                window.HTMLTextAreaElement.prototype, 'value'
            ).set;
            nativeSetter.call(ta, text);
            ta.dispatchEvent(new Event('input', { bubbles: true }));
        }""", prompt)
        time.sleep(0.5)

    print(f"  Prompt entered ({len(prompt)} chars, {prompt.count(chr(10))} lines)")

    if dry_run:
        page.screenshot(path=str(OUTPUT / f"test_{name}.png"))
        print(f"  DRY RUN — screenshot saved")
        page.close()
        return True

    # Record pre-existing image URLs (uploaded photo) to exclude from results
    pre_existing = set()
    for img in page.query_selector_all("img"):
        src = img.get_attribute("src") or ""
        if "assets.grok.com" in src:
            pre_existing.add(src)

    # 3. Submit — use JS to click the hidden submit button
    textarea.focus()
    time.sleep(0.5)
    result = page.evaluate("""() => {
        for (const label of ['Absenden', 'Submit', 'Send', 'Senden']) {
            const btn = document.querySelector(`button[aria-label="${label}"]`);
            if (btn) { btn.click(); return label; }
        }
        // Fallback: find any submit-like button
        const btns = document.querySelectorAll('button');
        for (const b of btns) {
            const svg = b.querySelector('svg');
            if (svg && b.closest('form, [class*="input"], [class*="chat"]')) {
                b.click();
                return 'svg-button';
            }
        }
        return null;
    }""")
    if result:
        print(f"  Submitted via '{result}' button")
    else:
        textarea.press("Enter")
        print("  Submitted via Enter key (fallback)")

    # 4. Wait for generated images (up to 3 min)
    found = []
    for tick in range(36):
        time.sleep(5)
        elapsed = (tick + 1) * 5

        for img in page.query_selector_all("img"):
            src = img.get_attribute("src") or ""
            if "assets.grok.com" in src and ("/generated/" in src or "/content" in src) and src not in found and src not in pre_existing:
                try:
                    w = img.evaluate("el => el.naturalWidth") or 0
                    h = img.evaluate("el => el.naturalHeight") or 0
                    if w > 100:
                        found.append(src)
                        print(f"  Image found: {w}x{h} at {elapsed}s")
                except:
                    found.append(src)
                    print(f"  Image found at {elapsed}s")

        if found and tick > 6:
            time.sleep(5)  # grace period for additional images
            for img in page.query_selector_all("img"):
                src = img.get_attribute("src") or ""
                if "assets.grok.com" in src and ("/generated/" in src or "/content" in src) and src not in found and src not in pre_existing:
                    found.append(src)
            break

        if tick > 0 and tick % 6 == 0:
            print(f"  Waiting... ({elapsed}s)")
            # Check for rate limit message
            try:
                body_text = page.inner_text("body")
                if "Limit" in body_text and ("zurückgesetzt" in body_text or "reset" in body_text.lower()):
                    print(f"  RATE LIMITED: {[l for l in body_text.split(chr(10)) if 'Limit' in l or 'limit' in l][0]}")
                    page.screenshot(path=str(OUTPUT / f"debug_{name}_ratelimit.png"))
                    page.close()
                    return False
            except:
                pass

    if not found:
        print(f"  FAIL: No images after 5 min")
        # Log what Grok actually responded with
        try:
            text = page.inner_text("body")[:1000]
            print(f"  Page text: {text[:300]}")
        except:
            pass
        page.screenshot(path=str(OUTPUT / f"debug_{name}_timeout.png"), full_page=True)
        page.close()
        return False

    # 5. Download
    for i, src in enumerate(found):
        suffix = "" if i == 0 else f"_alt{i}"
        out_path = OUTPUT / f"{name}{suffix}.jpg"
        try:
            # Download via page fetch (includes cookies/auth)
            b64_data = page.evaluate("""async (url) => {
                const resp = await fetch(url, { credentials: 'include' });
                if (!resp.ok) return null;
                const blob = await resp.blob();
                return new Promise(r => {
                    const reader = new FileReader();
                    reader.onloadend = () => r(reader.result);
                    reader.readAsDataURL(blob);
                });
            }""", src)
            if b64_data and b64_data.startswith("data:"):
                raw = base64.b64decode(b64_data.split(",", 1)[1])
                out_path.write_bytes(raw)
                print(f"  SAVED: {out_path.name} ({len(raw)//1024}KB)")
            else:
                print(f"  Download returned empty for {src[:60]}")
        except Exception as e:
            print(f"  Download error: {e}")
            (OUTPUT / f"{name}{suffix}_url.txt").write_text(src)
            print(f"  URL saved instead")

    page.close()
    return True


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    mode = sys.argv[1] if len(sys.argv) > 1 else "test"

    with sync_playwright() as p:
        # Try existing Chrome first
        browser = None
        for port in [9222, 9333, 40967]:
            try:
                browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
                print(f"Connected to Chrome on port {port}")
                break
            except:
                continue

        if browser:
            context = browser.contexts[0]
        else:
            print("No Chrome found — launching new browser (persistent profile)")
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(Path.home() / ".cache" / "printcraft-chrome"),
                headless=False,
                args=["--no-sandbox"],
            )

        if mode == "test":
            generate_scene(context, SCENES[0], dry_run=True)
        elif mode == "all":
            results = {}
            for scene in SCENES:
                ok = generate_scene(context, scene)
                results[scene["name"]] = "OK" if ok else "FAIL"
                time.sleep(3)
            print(f"\n{'='*60}")
            print("RESULTS:")
            for k, v in results.items():
                print(f"  {k}: {v}")
        else:
            start = int(mode)
            end = int(sys.argv[2]) if len(sys.argv) > 2 else start
            results = {}
            for i in range(start, end + 1):
                try:
                    ok = generate_scene(context, SCENES[i])
                    results[SCENES[i]["name"]] = "OK" if ok else "FAIL"
                except Exception as e:
                    print(f"  CRASH: {e}")
                    results[SCENES[i]["name"]] = "CRASH"
                time.sleep(3)
            print(f"\n{'='*60}")
            print("RESULTS:")
            for k, v in results.items():
                print(f"  {k}: {v}")

        if not browser:
            context.close()


if __name__ == "__main__":
    main()
