#!/usr/bin/env python3
"""Generate images on grok.com and save via element screenshot."""

import asyncio
import sys
import os
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


async def generate_scene(context, scene_index):
    scene = SCENES[scene_index]
    print(f"\n{'='*60}")
    print(f"[{scene_index+1}/6] {scene['name']}")
    print(f"{'='*60}")

    page = await context.new_page()
    await page.goto("https://grok.com/", wait_until="domcontentloaded", timeout=60000)
    await asyncio.sleep(10)

    # Find text input
    input_el = None
    for sel in ['[data-placeholder]', 'div[contenteditable="true"]', 'textarea', '[role="textbox"]']:
        try:
            input_el = await page.wait_for_selector(sel, timeout=5000)
            if input_el:
                break
        except:
            continue

    if not input_el:
        print("ERROR: No input!")
        await page.close()
        return None

    # Upload files
    file_inputs = await page.query_selector_all('input[type="file"]')
    if file_inputs:
        await file_inputs[0].set_input_files([STYLE_REF, scene['photo']])
        await asyncio.sleep(3)
        print("Uploaded")

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

    # Wait for generation and download via screenshot
    for attempt in range(90):
        await asyncio.sleep(5)
        imgs = await page.query_selector_all('img')
        gen_imgs = []
        for img in imgs:
            src = await img.get_attribute('src') or ''
            if 'assets.grok.com' in src and '/generated/' in src:
                gen_imgs.append((img, src))

        if gen_imgs and attempt > 10:
            # Give it extra time for full render
            await asyncio.sleep(3)
            print(f"Found {len(gen_imgs)} image(s) at {(attempt+1)*5}s")
            
            # Download each via element screenshot (most reliable)
            for i, (img, src) in enumerate(gen_imgs):
                suffix = f"_alt" if i > 0 else ""
                path = f"{OUTPUT_DIR}/{scene['name']}{suffix}.png"
                
                # First try: click to expand/get full res, then screenshot
                try:
                    # Get natural dimensions
                    dims = await page.evaluate("""
                        (img) => ({ w: img.naturalWidth, h: img.naturalHeight, src: img.src })
                    """, img)
                    print(f"  Image {i}: {dims['w']}x{dims['h']} natural")
                    print(f"  URL: {dims['src'][:100]}")
                    
                    # Save the URL for manual download
                    url_path = f"{OUTPUT_DIR}/{scene['name']}{suffix}_url.txt"
                    with open(url_path, 'w') as f:
                        f.write(dims['src'])
                    
                    # Screenshot the element
                    await img.screenshot(path=path)
                    size = os.path.getsize(path)
                    print(f"  Saved screenshot: {path} ({size//1024}KB)")
                    
                except Exception as e:
                    print(f"  Error: {e}")
            
            # DON'T close page - keep it open
            return page
        
        if attempt % 6 == 0 and attempt > 0:
            print(f"  Waiting... ({(attempt+1)*5}s)")

    print("Timeout - no images found")
    await page.screenshot(path=f"{OUTPUT_DIR}/debug_{scene['name']}_timeout.png", full_page=True)
    return None


async def main():
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    end = int(sys.argv[2]) if len(sys.argv) > 2 else len(SCENES)

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(CDP_URL)
        context = browser.contexts[0]
        print(f"Connected. Scenes {start}-{end-1}")

        pages_with_images = []
        for i in range(start, end):
            page = await generate_scene(context, i)
            if page:
                pages_with_images.append((SCENES[i]['name'], page))
            await asyncio.sleep(3)

        # Now try to download full-res from all kept pages
        print(f"\n\n{'='*60}")
        print(f"Attempting full-res downloads from {len(pages_with_images)} pages...")
        print(f"{'='*60}")
        
        for name, page in pages_with_images:
            imgs = await page.query_selector_all('img')
            for img in imgs:
                src = await img.get_attribute('src') or ''
                if 'assets.grok.com' in src and '/generated/' in src:
                    # Try clicking image to get full-res view
                    try:
                        await img.click()
                        await asyncio.sleep(2)
                        # Check for expanded/lightbox image
                        expanded = await page.query_selector('[class*="lightbox"] img, [class*="modal"] img, [class*="expanded"] img, [role="dialog"] img')
                        if expanded:
                            exp_src = await expanded.get_attribute('src') or ''
                            print(f"  Expanded image found: {exp_src[:80]}")
                            await expanded.screenshot(path=f"{OUTPUT_DIR}/{name}_fullres.png")
                            size = os.path.getsize(f"{OUTPUT_DIR}/{name}_fullres.png")
                            print(f"  Full-res screenshot: {size//1024}KB")
                            # Close lightbox
                            await page.keyboard.press('Escape')
                            await asyncio.sleep(1)
                    except Exception as e:
                        print(f"  Expand attempt: {e}")

        print("\nDONE!")
        print("Check URL files for manual download if screenshots are low-res:")
        for name, _ in pages_with_images:
            url_file = f"{OUTPUT_DIR}/{name}_url.txt"
            if os.path.exists(url_file):
                with open(url_file) as f:
                    print(f"  {name}: {f.read().strip()[:100]}")


asyncio.run(main())
