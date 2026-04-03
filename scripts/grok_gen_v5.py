#!/usr/bin/env python3
"""
Grok image generation v5 — simplified.
Uses Playwright to automate grok.com image generation.
Run with: python3 grok_gen_v5.py [start_index] [end_index]
Defaults: all 7 scenes (0-6)
"""

import sys
import time
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = Path("/home/g/Dokumente/Duschwand")
SOURCE = BASE / "00-source-photos"
OUTPUT = BASE / "07-grok-v4-retro-poster"

PHOTOS = [
    ("1.png", "bild1_hero_teal_bap670"),
    ("2.png", "bild2_white_italian"),
    ("3.png", "bild3_teal_kd"),
    ("4.png", "bild4_blue_abn274"),
    ("5.png", "bild5_hydrofoil_dog"),
    ("6.png", "bild6_jetranger"),
    ("7.png", "bild7_vw_van"),
]

PROMPT = """Transform this photo into a 1960s Italian travel poster illustration.

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
- Leave generous space around the subject on all sides"""


def run(start=0, end=6):
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        print(f"Connected. Processing scenes {start}-{end}\n")

        for idx in range(start, end + 1):
            photo_file, output_name = PHOTOS[idx]
            photo_path = str(SOURCE / photo_file)
            print(f"{'='*60}")
            print(f"[{idx+1}/7] {output_name}")
            print(f"{'='*60}")

            # Open new Grok conversation
            page = context.new_page()
            page.goto("https://grok.com/", wait_until="networkidle", timeout=30000)
            time.sleep(3)

            # Find input and upload photo
            try:
                # Look for file input
                file_inputs = page.query_selector_all('input[type="file"]')
                if file_inputs:
                    file_inputs[0].set_input_files(photo_path)
                    print("  Photo uploaded via file input")
                    time.sleep(2)
                else:
                    print("  ERROR: No file input found!")
                    page.close()
                    continue
            except Exception as e:
                print(f"  Upload error: {e}")
                page.close()
                continue

            # Enter prompt via clipboard paste (keyboard.type sends Enter on newlines!)
            try:
                editor = page.query_selector('div[contenteditable="true"]') or \
                         page.query_selector('[data-placeholder]') or \
                         page.query_selector('textarea')
                if not editor:
                    print("  ERROR: No input found!")
                    page.close()
                    continue
                editor.click()
                time.sleep(0.5)
                # Use evaluate to set clipboard and paste — avoids newline=Enter problem
                page.evaluate("""(text) => {
                    const dt = new DataTransfer();
                    dt.setData('text/plain', text);
                    const el = document.querySelector('div[contenteditable="true"]') ||
                               document.querySelector('textarea');
                    if (el) {
                        el.focus();
                        const event = new ClipboardEvent('paste', {
                            clipboardData: dt,
                            bubbles: true,
                            cancelable: true
                        });
                        el.dispatchEvent(event);
                    }
                }""", PROMPT)
                time.sleep(1)
                # Verify text was inserted — if not, fall back to fill()
                content = editor.inner_text().strip() if editor.inner_text else ""
                if len(content) < 50:
                    print("  Paste didn't work, trying fill()...")
                    # For textarea
                    ta = page.query_selector('textarea')
                    if ta:
                        ta.fill(PROMPT)
                    else:
                        # Last resort: set innerHTML for contenteditable
                        escaped = PROMPT.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')
                        page.evaluate(f"""() => {{
                            const el = document.querySelector('div[contenteditable="true"]');
                            if (el) {{
                                el.innerText = `{escaped}`;
                                el.dispatchEvent(new Event('input', {{bubbles: true}}));
                            }}
                        }}""")
                    time.sleep(1)
                print("  Prompt entered")
                time.sleep(1)
            except Exception as e:
                print(f"  Prompt error: {e}")
                page.close()
                continue

            # Submit — find and click the send button explicitly
            try:
                send_btn = None
                # Try multiple selectors for the send/submit button
                for sel in [
                    'button[aria-label="Submit"]',
                    'button[aria-label="Send"]',
                    'button[data-testid="send-button"]',
                    'button[type="submit"]',
                ]:
                    send_btn = page.query_selector(sel)
                    if send_btn:
                        break
                if not send_btn:
                    # Try finding button near the input area
                    buttons = page.query_selector_all('button')
                    for b in buttons:
                        aria = b.get_attribute('aria-label') or ''
                        if any(w in aria.lower() for w in ['send', 'submit', 'go']):
                            send_btn = b
                            break
                if send_btn:
                    send_btn.click()
                    print("  Submitted via button")
                else:
                    # Absolute last resort
                    page.keyboard.press("Control+Enter")
                    print("  Submitted via Ctrl+Enter")
                time.sleep(5)
            except Exception as e:
                print(f"  Submit error: {e}")

            # Wait for generated image (up to 3 minutes)
            found_images = []
            for wait in range(18):  # 18 * 10s = 180s max
                time.sleep(10)
                elapsed = (wait + 1) * 10 + 5
                
                # Look for grok asset images
                imgs = page.query_selector_all('img[src*="assets.grok.com"]')
                new_imgs = []
                for img in imgs:
                    src = img.get_attribute("src") or ""
                    if "generated" in src and src not in [x[0] for x in found_images]:
                        w = img.evaluate("el => el.naturalWidth") or 0
                        h = img.evaluate("el => el.naturalHeight") or 0
                        if w > 200:
                            new_imgs.append((src, w, h))

                if new_imgs:
                    found_images.extend(new_imgs)
                    print(f"  Found {len(new_imgs)} image(s) at {elapsed}s")
                    # Wait a bit more for potential second image
                    time.sleep(10)
                    # Check again
                    imgs2 = page.query_selector_all('img[src*="assets.grok.com"]')
                    for img in imgs2:
                        src = img.get_attribute("src") or ""
                        if "generated" in src and src not in [x[0] for x in found_images]:
                            w = img.evaluate("el => el.naturalWidth") or 0
                            h = img.evaluate("el => el.naturalHeight") or 0
                            if w > 200:
                                found_images.append((src, w, h))
                    break
                else:
                    print(f"  Waiting... ({elapsed}s)")

            if not found_images:
                print(f"  FAIL: No images found after 3 minutes")
                page.screenshot(path=str(OUTPUT / f"{output_name}_FAIL.png"))
                page.close()
                continue

            # Download images
            for i, (src, w, h) in enumerate(found_images):
                suffix = "" if i == 0 else f"_alt{i}"
                out_path = OUTPUT / f"{output_name}{suffix}.jpg"
                try:
                    response = page.request.get(src)
                    if response.ok:
                        out_path.write_bytes(response.body())
                        size_kb = len(response.body()) // 1024
                        print(f"  SAVED: {out_path.name} ({w}x{h}, {size_kb}KB)")
                    else:
                        print(f"  Download failed: HTTP {response.status}")
                except Exception as e:
                    # Fallback: screenshot the image element
                    print(f"  Download error: {e}, trying screenshot...")
                    for img in page.query_selector_all('img[src*="assets.grok.com"]'):
                        if img.get_attribute("src") == src:
                            img.screenshot(path=str(out_path))
                            print(f"  SAVED (screenshot): {out_path.name}")
                            break

            page.close()
            time.sleep(2)

        print(f"\n{'='*60}")
        print("DONE!")
        print(f"{'='*60}")


if __name__ == "__main__":
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    end = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    run(start, end)
