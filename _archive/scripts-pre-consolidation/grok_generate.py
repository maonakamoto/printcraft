#!/usr/bin/env python3
"""Connect to Brave via CDP and generate images on grok.com."""

import asyncio
import sys
import os
import base64
import re
from playwright.async_api import async_playwright

CDP_URL = "http://127.0.0.1:9333"
BASE = "/home/g/Dokumente/Duschwand"
STYLE_REF = f"{BASE}/7photos-edited/grok_3_red_amph.png"
OUTPUT_DIR = f"{BASE}/7photos-edited"

SCENES = [
    {
        "name": "grok_1_hero_v2",
        "photo": f"{BASE}/7photos real/1.png",
        "prompt": 'I am uploading TWO images. Image 1 is a STYLE REFERENCE (a red Amphicar painting) — copy ONLY the art style, NOT the red color. Image 2 is the SOURCE PHOTO to recreate. Recreate the source photo in the exact art style of the reference: semi-realistic gouache-style digital painting, smooth strokes, NO black outlines, warm golden-hour palette, glossy reflective paint, stylized water with wake splash, sunset sky. CRITICAL: The car must be TEAL/TURQUOISE (NOT red!) — match the exact color from the source photo. This is an Amphicar 770 with license plate B-AP 670. Three people aboard — preserve their exact faces, expressions, hair, clothing, poses from the source photo. Gold chrome stripes, chrome bumpers, Amphicar tail fins. Water spray and wake. BLACK BACKGROUND above the waterline. No text, no watermarks.'
    },
    {
        "name": "grok_2_white_v2",
        "photo": f"{BASE}/7photos real/2.png",
        "prompt": 'I am uploading TWO images. Image 1 is a STYLE REFERENCE (a red Amphicar painting) — copy ONLY the art style, NOT the color. Image 2 is the SOURCE PHOTO to recreate. Recreate the source photo in the exact art style of the reference: semi-realistic gouache-style digital painting, smooth strokes, NO black outlines, warm golden-hour palette, glossy reflective paint, stylized water with wake splash, sunset sky. CRITICAL: The car must be WHITE with red stripe accents (NOT red!) — match the exact colors from the source photo. This is a white Amphicar 770 with Italian flag. Two people aboard (one wearing stripy pants) — preserve their exact faces, expressions, hair, clothing from the source photo. Chrome bumpers, Amphicar tail fins. Water spray and wake. BLACK BACKGROUND above the waterline. No text, no watermarks.'
    },
    {
        "name": "grok_4_blue_v2",
        "photo": f"{BASE}/7photos real/4.png",
        "prompt": 'I am uploading TWO images. Image 1 is a STYLE REFERENCE (a red Amphicar painting) — copy ONLY the art style, NOT the color. Image 2 is the SOURCE PHOTO to recreate. Recreate the source photo in the exact art style of the reference: semi-realistic gouache-style digital painting, smooth strokes, NO black outlines, warm golden-hour palette, glossy reflective paint, stylized water with wake splash, sunset sky. CRITICAL: The car must be LIGHT BLUE/PASTEL BLUE (NOT red!) — match the exact color from the source photo. This is a light blue Amphicar 770 with license plate AB-N 274. Two people aboard in a Titanic-like pose — preserve their exact faces, expressions, hair, clothing from the source photo. Chrome bumpers, Amphicar tail fins. Water spray and wake. BLACK BACKGROUND above the waterline. No text, no watermarks.'
    },
    {
        "name": "grok_5_hydrofoil_v2",
        "photo": f"{BASE}/7photos real/5.png",
        "prompt": 'I am uploading TWO images. Image 1 is a STYLE REFERENCE (a red Amphicar painting) — copy ONLY the art style. Image 2 is the SOURCE PHOTO to recreate. Recreate the source photo in the exact art style of the reference: semi-realistic gouache-style digital painting, smooth strokes, NO black outlines, warm golden-hour palette, glossy surfaces, stylized water with spray, sunset sky. Subject: A person on a hydrofoil board on a lake at golden hour, with a golden retriever/dog. Preserve their exact face, expression, hair, clothing, pose from the source photo. Dynamic water spray, foil lifting above the surface. BLACK BACKGROUND above the waterline. No text, no watermarks.'
    },
    {
        "name": "grok_6_jetranger_v2",
        "photo": f"{BASE}/7photos real/6.png",
        "prompt": 'I am uploading TWO images. Image 1 is a STYLE REFERENCE (a red Amphicar painting) — copy ONLY the art style, NOT the color. Image 2 is the SOURCE PHOTO to recreate. Recreate the source photo in the exact art style of the reference: semi-realistic gouache-style digital painting, smooth strokes, NO black outlines, warm golden-hour palette, glossy surfaces, stylized water, sunset sky. CRITICAL: The vehicle must be BLUE (NOT red!) — match the exact color from the source photo. This is a blue amphibious vehicle/truck marked "66568 JETRANGER" with a Dutch flag. Man with arms spread wide and passengers aboard — preserve their exact faces, expressions, hair, clothing from the source photo. Water spray around the hull. BLACK BACKGROUND above the waterline. No text, no watermarks.'
    },
    {
        "name": "grok_7_vv_van_v2",
        "photo": f"{BASE}/7photos real/7.png",
        "prompt": 'I am uploading TWO images. Image 1 is a STYLE REFERENCE (a red Amphicar painting) — copy ONLY the art style, NOT the color. Image 2 is the SOURCE PHOTO to recreate. Recreate the source photo in the exact art style of the reference: semi-realistic gouache-style digital painting, smooth strokes, NO black outlines, warm golden-hour palette, glossy surfaces, stylized water, sunset sky. CRITICAL: The vehicle must be WHITE (NOT red!) — match the exact color from the source photo. This is a white amphibious VW-type van. Woman sitting on the roof in a chair, couple visible inside — preserve their exact faces, expressions, hair, clothing from the source photo. Water wake and reflections. BLACK BACKGROUND above the waterline. No text, no watermarks.'
    },
]


async def download_image(page, url, output_path):
    """Download an image from URL via the page context (handles auth cookies)."""
    try:
        img_data = await page.evaluate(f"""
            async () => {{
                const resp = await fetch('{url}');
                const blob = await resp.blob();
                return new Promise((resolve) => {{
                    const reader = new FileReader();
                    reader.onloadend = () => resolve(reader.result);
                    reader.readAsDataURL(blob);
                }});
            }}
        """)
        if img_data and img_data.startswith('data:'):
            b64 = img_data.split(',', 1)[1]
            img_bytes = base64.b64decode(b64)
            with open(output_path, 'wb') as f:
                f.write(img_bytes)
            print(f"  SAVED: {output_path} ({len(img_bytes)//1024}KB)")
            return True
    except Exception as e:
        print(f"  Download error: {e}")
    return False


async def generate_scene(context, scene_index):
    scene = SCENES[scene_index]
    print(f"\n{'='*60}")
    print(f"[{scene_index+1}/6] Generating: {scene['name']}")
    print(f"{'='*60}")

    page = await context.new_page()
    await page.goto("https://grok.com/", wait_until="domcontentloaded", timeout=60000)
    await asyncio.sleep(8)

    # Find text input
    input_el = None
    for selector in ['[data-placeholder]', 'div[contenteditable="true"]', 'textarea', '[role="textbox"]', '.ProseMirror']:
        try:
            input_el = await page.wait_for_selector(selector, timeout=5000)
            if input_el:
                print(f"Found input: {selector}")
                break
        except:
            continue

    if not input_el:
        print("ERROR: No input field!")
        await page.screenshot(path=f"{OUTPUT_DIR}/debug_{scene['name']}_fail.png")
        await page.close()
        return False

    # Upload files
    file_inputs = await page.query_selector_all('input[type="file"]')
    if file_inputs:
        await file_inputs[0].set_input_files([STYLE_REF, scene['photo']])
        await asyncio.sleep(3)
        print("Files uploaded")
    else:
        print("WARNING: No file input!")

    # Enter prompt via clipboard
    await input_el.click()
    await asyncio.sleep(0.3)
    await page.evaluate("text => navigator.clipboard.writeText(text)", scene['prompt'])
    await page.keyboard.press('Control+v')
    await asyncio.sleep(1)
    
    # Verify text was pasted
    text = await input_el.text_content() or ''
    if len(text.strip()) < 50:
        print("Paste failed, using fill()...")
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
        print("Submitted via button")
    else:
        await page.keyboard.press('Enter')
        print("Submitted via Enter")

    # Wait for generation
    print("Waiting for Grok to generate...")
    found_urls = []

    for attempt in range(90):  # up to 7.5 min
        await asyncio.sleep(5)

        # Look for assets.grok.com image URLs
        imgs = await page.query_selector_all('img')
        for img in imgs:
            src = await img.get_attribute('src') or ''
            if 'assets.grok.com' in src and '/generated/' in src:
                if src not in found_urls:
                    found_urls.append(src)
                    box = await img.bounding_box()
                    w = box['width'] if box else 0
                    h = box['height'] if box else 0
                    print(f"  Found generated image! ({w:.0f}x{h:.0f})")

        # Grok often generates 2 variants — wait a bit for both
        if found_urls and attempt > 10:
            # Check if generation seems complete (no more loading indicators)
            loading = await page.query_selector('[class*="loading"], [class*="spinner"], [class*="generating"]')
            if not loading or attempt > 20:
                break

        if attempt % 6 == 0 and attempt > 0:
            print(f"  Still waiting... ({(attempt+1)*5}s)")

    if found_urls:
        print(f"\nFound {len(found_urls)} generated image(s)")
        for i, url in enumerate(found_urls):
            output_path = f"{OUTPUT_DIR}/{scene['name']}{'_alt' if i > 0 else ''}.png"
            await download_image(page, url, output_path)
    else:
        print("No generated images found!")
        await page.screenshot(path=f"{OUTPUT_DIR}/debug_{scene['name']}_timeout.png", full_page=True)

    await page.close()
    return bool(found_urls)


async def main():
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    end = int(sys.argv[2]) if len(sys.argv) > 2 else len(SCENES)

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(CDP_URL)
        contexts = browser.contexts
        context = contexts[0] if contexts else await browser.new_context()
        print(f"Connected to Brave. Processing scenes {start} to {end-1}")

        results = {}
        for i in range(start, end):
            success = await generate_scene(context, i)
            results[SCENES[i]['name']] = 'OK' if success else 'FAILED'
            await asyncio.sleep(5)

        print(f"\n\n{'='*60}")
        print("RESULTS:")
        for name, status in results.items():
            print(f"  {name}: {status}")
        print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())
