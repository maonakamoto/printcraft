#!/usr/bin/env python3
"""Generate via Grok Chat - use hidden file input directly."""
import asyncio
import sys
import time
from pathlib import Path
from playwright.async_api import async_playwright

CDP_URL = "http://127.0.0.1:9223"
OUTPUT_DIR = Path("/home/g/dev/printcraft/projects/duschwand-roli/generated/round1-grok")

IMAGES = [
    "/home/g/Dokumente/Duschwand/WhatsApp Image 2025-12-21 at 12.31.53.jpeg",
    "/home/g/Dokumente/Duschwand/WhatsApp Image 2025-12-31 at 10.14.146.jpeg",
    "/home/g/Dokumente/Duschwand/ChatGPT Image 17. März 2026, 12_12_26.png",
]

PROMPT = """I need you to generate a cartoon illustration based on these reference images.

Image 1: Real photo of a couple (Roli and his girlfriend) in a blue Amphicar on the water - these are the MAIN characters
Image 2: The blue Amphicar amphibious vehicle driving through water with friends
Image 3: A cartoon style reference showing the look we want

Please CREATE/GENERATE an image:
- A vibrant Pixar-style cartoon of Roli and his girlfriend (from image 1) in the blue Amphicar driving through a sunny lake
- Their faces should be recognizable from image 1
- Around them, 6 friends in various boats, jet skis, kayaks
- Bold colors, sparkling blue water, green hills, blue sky with fluffy clouds
- Fun, celebratory party-on-water atmosphere
- Square 1:1 composition for a large wall mural"""

async def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(CDP_URL)
        context = browser.contexts[0]

        page = None
        for pg in context.pages:
            if "grok.com" in pg.url:
                page = pg
                break
        if not page:
            page = await context.new_page()

        await page.goto("https://grok.com", wait_until="networkidle", timeout=30000)
        await asyncio.sleep(3)

        # Upload via hidden file input
        print("Uploading images via file input...")
        file_input = await page.query_selector('input[type="file"]')
        if file_input:
            await file_input.set_input_files(IMAGES)
            print(f"  Uploaded {len(IMAGES)} images")
            await asyncio.sleep(5)
        else:
            print("  ERROR: No file input found")
            return

        # Take screenshot to verify upload
        await page.screenshot(path=str(OUTPUT_DIR / "00_uploaded.png"))

        # Paste prompt via clipboard (keyboard.type sends Enter for newlines which submits!)
        print("Pasting prompt via clipboard...")
        typed = False

        # Find visible editor and focus it
        editors = await page.query_selector_all('[contenteditable="true"]')
        for ed in editors:
            if await ed.is_visible():
                await ed.click()
                await asyncio.sleep(0.3)
                typed = True
                break

        if not typed:
            textareas = await page.query_selector_all('textarea')
            for ta in textareas:
                if await ta.is_visible():
                    await ta.click()
                    await asyncio.sleep(0.3)
                    typed = True
                    break

        if not typed:
            await page.keyboard.press('Tab')
            await asyncio.sleep(0.3)

        # Use JavaScript to set clipboard and paste
        await page.evaluate("""(text) => {
            const el = document.querySelector('[contenteditable="true"]') || document.activeElement;
            if (el) {
                el.focus();
                // Insert text via execCommand (works in contenteditable)
                document.execCommand('insertText', false, text);
            }
        }""", PROMPT)
        print("  Pasted prompt via JS insertText")
        typed = True

        if not typed:
            print("  ERROR: Could not paste prompt")
            return

        await asyncio.sleep(1)
        await page.screenshot(path=str(OUTPUT_DIR / "01_ready.png"))

        # Submit
        print("Submitting...")
        submit = await page.query_selector('button[aria-label="Submit"]')
        if submit:
            disabled = await submit.get_attribute('disabled')
            if not disabled:
                await submit.click()
                print("  Clicked Submit")
            else:
                await page.keyboard.press('Control+Enter')
                print("  Ctrl+Enter (submit was disabled)")
        else:
            await page.keyboard.press('Control+Enter')
            print("  Ctrl+Enter (no submit button)")

        # Wait for generation
        print("Waiting for Grok response...")
        start = time.time()
        
        for i in range(90):  # 3 min max
            await asyncio.sleep(2)
            elapsed = time.time() - start

            # Check for completion: look for action buttons that appear after response
            # Grok shows "Copy", "Regenerate", "Thread" buttons when done
            regen = await page.query_selector('button:has-text("Regenerate")')
            thread = await page.query_selector('button:has-text("Thread")')
            
            if (regen or thread) and elapsed > 8:
                print(f"\n  Response complete! ({elapsed:.0f}s)")
                break
            
            if i % 10 == 0:
                print(f"  ...{elapsed:.0f}s")
                await page.screenshot(path=str(OUTPUT_DIR / f"02_wait_{i}.png"))

        await asyncio.sleep(3)
        
        # Final screenshot
        await page.screenshot(path=str(OUTPUT_DIR / "03_result.png"), full_page=True)
        print("  Saved result screenshot")

        # Try to find download buttons for generated images
        dl_buttons = await page.query_selector_all('button:has-text("Download")')
        print(f"  Found {len(dl_buttons)} download button(s)")
        
        for idx, btn in enumerate(dl_buttons):
            try:
                async with page.expect_download(timeout=15000) as dl_info:
                    await btn.click()
                download = await dl_info.value
                out = OUTPUT_DIR / f"generated_{idx}.png"
                await download.save_as(str(out))
                print(f"  Downloaded: {out}")
                await asyncio.sleep(2)
            except Exception as e:
                print(f"  Download {idx} failed: {e}")

        # Also try to extract image URLs from the page
        imgs = await page.query_selector_all('img')
        for img in imgs:
            src = await img.get_attribute('src') or ''
            if src.startswith('https://') and ('pbs.twimg' in src or 'assets.grok' in src):
                bbox = await img.bounding_box()
                if bbox and bbox['width'] > 300:
                    print(f"  Large image found: {src[:120]}")

        print(f"\nDone! Check: {OUTPUT_DIR}")

asyncio.run(main())
