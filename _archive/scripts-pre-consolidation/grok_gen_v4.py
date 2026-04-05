#!/usr/bin/env python3
"""Generate v3 images on grok.com — cartoonish retro 60s comic style."""

import asyncio
import sys
import os
import base64
from playwright.async_api import async_playwright

CDP_URL = "http://127.0.0.1:9333"
BASE = "/home/g/Dokumente/Duschwand"
OUTPUT_DIR = f"{BASE}/7photos-edited"

STYLE_BLOCK = """Style: RETRO 1960s CARTOON ILLUSTRATION. Think vintage American travel posters, classic car advertisements, 60s diner art, Hanna-Barbera meets European comic books. 
KEY STYLE REQUIREMENTS:
- BOLD BLACK OUTLINES on everything (people, car, water splashes)
- FLAT COLOR AREAS with limited shading (cel-shaded, not photorealistic)
- EXAGGERATED, slightly caricatured but recognizable faces
- SATURATED, punchy retro colors (like vintage print posters)
- Warm golden sunset palette — peach, amber, orange, turquoise water
- Simplified but charming rendering — NOT photorealistic, NOT painterly
- Visible ink-like linework, confident strokes
- Water rendered as stylized splashes and curves, not realistic ripples
- Think: if this were screen-printed on a retro poster in 1965"""

SCENES = [
    {
        "name": "grok_1_hero_v3",
        "photo": f"{BASE}/7photos real/1.png",
        "prompt": f"""Turn this photo into a retro cartoon illustration. {STYLE_BLOCK}

Subject: A TEAL/TURQUOISE Amphicar 770 (amphibious car) with license plate B-AP 670 cruising on a lake at golden hour. THREE people aboard — recreate their EXACT faces, expressions, hair, clothing, hats, sunglasses from the photo but in cartoon style (recognizable caricatures). Gold chrome stripes, chrome bumpers, distinctive Amphicar tail fins. Stylized water spray and wake.

BLACK BACKGROUND above the waterline/horizon. No text, no watermarks."""
    },
    {
        "name": "grok_2_white_v3",
        "photo": f"{BASE}/7photos real/2.png",
        "prompt": f"""Turn this photo into a retro cartoon illustration. {STYLE_BLOCK}

Subject: A WHITE Amphicar 770 with red stripe accents and Italian flag, cruising on a lake at golden hour. TWO people aboard — CAREFULLY recreate their EXACT appearance from the photo: one person wears STRIPY PANTS (this is a key detail!), preserve their exact faces, hair, clothing, poses as cartoon caricatures. Chrome bumpers, Amphicar tail fins. Stylized water spray and wake.

IMPORTANT: Look at the photo very carefully for the people's clothing and accessories. The stripy pants person is distinctive — get this right.

BLACK BACKGROUND above the waterline/horizon. No text, no watermarks."""
    },
    {
        "name": "grok_4_blue_v3",
        "photo": f"{BASE}/7photos real/4.png",
        "prompt": f"""Turn this photo into a retro cartoon illustration. {STYLE_BLOCK}

Subject: A LIGHT BLUE/PASTEL BLUE Amphicar 770 with license plate AB-N 274 cruising on a lake at golden hour. TWO people in a Titanic-like pose (arms spread) — recreate their EXACT faces, expressions, hair, clothing from the photo as cartoon caricatures. Chrome bumpers, Amphicar tail fins. Stylized water spray and wake.

BLACK BACKGROUND above the waterline/horizon. No text, no watermarks."""
    },
    {
        "name": "grok_5_hydrofoil_v3",
        "photo": f"{BASE}/7photos real/5.png",
        "prompt": f"""Turn this photo into a retro cartoon illustration. {STYLE_BLOCK}

Subject: A person riding a HYDROFOIL BOARD on a lake at golden hour, with a GOLDEN RETRIEVER DOG. Recreate their exact face, expression, hair, clothing, pose from the photo as a cartoon caricature. Dynamic stylized water spray, foil lifting above the surface. The dog should be cute and cartoonish.

BLACK BACKGROUND above the waterline/horizon. No text, no watermarks."""
    },
    {
        "name": "grok_6_jetranger_v3",
        "photo": f"{BASE}/7photos real/6.png",
        "prompt": f"""Turn this photo into a retro cartoon illustration. {STYLE_BLOCK}

Subject: A BLUE amphibious vehicle/truck with "66568 JETRANGER" written on it, with a DUTCH FLAG. A man stands with ARMS SPREAD WIDE, other passengers aboard — recreate their exact faces, expressions, hair, clothing from the photo as cartoon caricatures. Stylized water spray around the hull.

BLACK BACKGROUND above the waterline/horizon. No text, no watermarks."""
    },
    {
        "name": "grok_7_vv_van_v3",
        "photo": f"{BASE}/7photos real/7.png",
        "prompt": f"""Turn this photo into a retro cartoon illustration. {STYLE_BLOCK}

Subject: A WHITE amphibious VW-type van/vehicle on water at golden hour. A WOMAN SITS ON THE ROOF in a chair, a couple visible inside the vehicle — recreate their exact faces, expressions, hair, clothing from the photo as cartoon caricatures. Stylized water wake and reflections.

BLACK BACKGROUND above the waterline/horizon. No text, no watermarks."""
    },
]


async def generate_scene(context, scene_index):
    scene = SCENES[scene_index]
    print(f"\n{'='*60}")
    print(f"[{scene_index+1}/6] {scene['name']}")
    print(f"{'='*60}")

    page = await context.new_page()
    await page.goto("https://grok.com/", wait_until="domcontentloaded", timeout=60000)
    await asyncio.sleep(15)

    # Find text input — retry with increasing waits
    input_el = None
    for attempt in range(3):
        for sel in ['[data-placeholder]', 'div[contenteditable="true"]', 'textarea', '[role="textbox"]', '.ProseMirror']:
            try:
                input_el = await page.wait_for_selector(sel, timeout=8000)
                if input_el:
                    break
            except:
                continue
        if input_el:
            break
        print(f"  Input not found, retrying ({attempt+1}/3)...")
        await asyncio.sleep(5)

    if not input_el:
        print("ERROR: No input! Saving debug screenshot...")
        await page.screenshot(path=f"{OUTPUT_DIR}/debug_{scene['name']}_noinput.png")
        await page.close()
        return None

    # Upload source photo only (no style reference — let the prompt drive the style)
    file_inputs = await page.query_selector_all('input[type="file"]')
    if file_inputs:
        await file_inputs[0].set_input_files([scene['photo']])
        await asyncio.sleep(3)
        print("Photo uploaded")

    # Enter prompt
    await input_el.click()
    await asyncio.sleep(0.3)
    try:
        await page.evaluate("text => navigator.clipboard.writeText(text)", scene['prompt'])
        await page.keyboard.press('Control+v')
        await asyncio.sleep(1)
    except:
        pass
    text = await input_el.text_content() or ''
    if len(text.strip()) < 50:
        await input_el.fill(scene['prompt'])
        await asyncio.sleep(0.5)
    print("Prompt entered")

    # Submit
    send_btn = None
    for sel in ['button[aria-label*="end"]', 'button[aria-label*="Send"]', 'button[type="submit"]']:
        send_btn = await page.query_selector(sel)
        if send_btn:
            break
    if send_btn:
        await send_btn.click()
    else:
        await page.keyboard.press('Enter')
    print("Submitted, waiting...")

    # Wait for generation
    found_urls = []
    for attempt in range(90):
        await asyncio.sleep(5)
        imgs = await page.query_selector_all('img')
        for img in imgs:
            src = await img.get_attribute('src') or ''
            if 'assets.grok.com' in src and '/generated/' in src and src not in found_urls:
                found_urls.append(src)
                dims = await page.evaluate("(img) => ({ w: img.naturalWidth, h: img.naturalHeight })", img)
                print(f"  Found image: {dims['w']}x{dims['h']}")

        if found_urls and attempt > 10:
            break

        if attempt % 6 == 0 and attempt > 0:
            print(f"  Waiting... ({(attempt+1)*5}s)")

    if found_urls:
        # Download via fetch
        for i, url in enumerate(found_urls):
            suffix = f"_alt" if i > 0 else ""
            try:
                result = await page.evaluate(f"""
                    async () => {{
                        const resp = await fetch('{url}', {{ credentials: 'include' }});
                        if (!resp.ok) return null;
                        const blob = await resp.blob();
                        return new Promise(r => {{
                            const reader = new FileReader();
                            reader.onloadend = () => r(reader.result);
                            reader.readAsDataURL(blob);
                        }});
                    }}
                """)
                if result and result.startswith('data:'):
                    b64 = result.split(',', 1)[1]
                    data = base64.b64decode(b64)
                    path = f"{OUTPUT_DIR}/{scene['name']}{suffix}.jpg"
                    with open(path, 'wb') as f:
                        f.write(data)
                    print(f"  SAVED: {path} ({len(data)//1024}KB)")
            except Exception as e:
                print(f"  Download error: {e}")
                # Fallback: save URL
                with open(f"{OUTPUT_DIR}/{scene['name']}{suffix}_url.txt", 'w') as f:
                    f.write(url)
    else:
        print("No images generated!")
        await page.screenshot(path=f"{OUTPUT_DIR}/debug_{scene['name']}_timeout.png", full_page=True)

    await page.close()
    return bool(found_urls)


async def main():
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    end = int(sys.argv[2]) if len(sys.argv) > 2 else len(SCENES)

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(CDP_URL)
        context = browser.contexts[0]
        print(f"Connected. Scenes {start}-{end-1}")

        results = {}
        for i in range(start, end):
            success = await generate_scene(context, i)
            results[SCENES[i]['name']] = 'OK' if success else 'FAIL'
            await asyncio.sleep(3)

        print(f"\n{'='*60}")
        print("RESULTS:")
        for name, status in results.items():
            print(f"  {name}: {status}")

asyncio.run(main())
