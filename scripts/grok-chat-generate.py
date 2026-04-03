#!/usr/bin/env python3
"""Generate artwork via Grok Chat (free tier) with image references."""

import asyncio
import sys
import time
import glob
from pathlib import Path
from playwright.async_api import async_playwright

CDP_URL = "http://127.0.0.1:9223"
OUTPUT_DIR = Path("/home/g/dev/printcraft/projects/duschwand-roli/generated/round1-grok")
REFS = Path("/home/g/Dokumente/Duschwand")

PROMPT = """I'm creating a large wall mural (200x193 cm) for a shower wall on a houseboat. I need you to generate a cartoon illustration.

Here's what I'm uploading:
- Image 1: A real photo of a couple (Roli and his girlfriend) in a blue Amphicar on the water - these are the MAIN subjects
- Image 2: Another photo of the blue Amphicar/amphibious vehicle in action on the water
- Image 3: An AI-generated cartoon that shows the STYLE we want (but the faces aren't recognizable enough)

Please generate a vibrant, fun cartoon illustration with these requirements:
1. CENTER: The couple from Image 1 (Roli driving, his girlfriend behind him with arms spread) in the blue Amphicar driving through a sunny lake. Their faces must be RECOGNIZABLE from the reference photo.
2. Around them: 6 other friends in various boats, jet skis, kayaks, and inflatables on the water
3. Style: Bold, vibrant cartoon like a Pixar movie poster - colorful, fun, celebratory
4. Setting: Sunny lake with blue sky, green hills, sparkling water
5. Square 1:1 composition
6. The blue Amphicar should look like the one in the photos (vintage convertible car that floats)

Make the faces realistic and recognizable while keeping the overall cartoon/illustration style."""

async def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    images_to_upload = [
        "/home/g/Dokumente/Duschwand/WhatsApp Image 2025-12-21 at 12.31.53.jpeg",  # Roli + gf in Amphicar
        "/home/g/Dokumente/Duschwand/WhatsApp Image 2025-12-31 at 10.14.146.jpeg",  # Amphicar in water
        "/home/g/Dokumente/Duschwand/ChatGPT Image 17. März 2026, 12_12_26.png",    # Cartoon style reference
    ]

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(CDP_URL)
        context = browser.contexts[0]
        
        # Find or create Grok tab
        page = None
        for pg in context.pages:
            if "grok.com" in pg.url:
                page = pg
                break
        if not page:
            page = await context.new_page()
        
        # Go to Grok chat (NOT imagine - chat is free)
        await page.goto("https://grok.com", wait_until="networkidle", timeout=30000)
        await asyncio.sleep(3)
        
        # Check login
        content = await page.content()
        logged_in = "Anmelden" not in content and "Sign in" not in content
        print(f"Logged in: {logged_in}")
        
        # Upload images via attach button
        print("Uploading reference images...")
        
        # Click attach
        attach = await page.query_selector('button[aria-label*="Anhängen"], button[aria-label*="Attach"]')
        if not attach:
            attach = await page.query_selector('button:has-text("Anhängen")')
        
        if attach:
            await attach.click()
            await asyncio.sleep(1)
            
            # Click "Datei hochladen" (file upload)
            upload_opt = await page.query_selector('[role="menuitem"]:has-text("Datei hochladen"), [role="menuitem"]:has-text("Upload file")')
            if upload_opt:
                # Arm file chooser before clicking
                try:
                    async with page.expect_file_chooser(timeout=10000) as fc_info:
                        await upload_opt.click()
                    file_chooser = await fc_info.value
                    await file_chooser.set_files(images_to_upload)
                    print(f"  Uploaded {len(images_to_upload)} files!")
                    await asyncio.sleep(5)
                except Exception as e:
                    print(f"  File chooser approach failed: {e}")
                    # Try hidden input approach
                    file_input = await page.query_selector('input[type="file"]')
                    if file_input:
                        await file_input.set_input_files(images_to_upload)
                        print("  Uploaded via hidden input!")
                        await asyncio.sleep(5)
                    else:
                        print("  ERROR: Cannot upload files")
                        return
            else:
                print("  No upload option found in menu")
                return
        else:
            # Try hidden input directly
            file_input = await page.query_selector('input[type="file"]')
            if file_input:
                await file_input.set_input_files(images_to_upload)
                print("  Uploaded via hidden input!")
                await asyncio.sleep(5)
            else:
                print("  ERROR: No attach button or file input found")
                return

        # Verify upload
        await page.screenshot(path=str(OUTPUT_DIR / "00_after_upload.png"))
        print("  Saved upload screenshot")
        
        # Type the prompt
        editor = await page.query_selector('[contenteditable]')
        if not editor:
            editor = await page.query_selector('textarea')
        
        if editor:
            await editor.click()
            await asyncio.sleep(0.5)
            # Type prompt (use fill for speed)
            await editor.fill("")
            await page.keyboard.type(PROMPT, delay=5)
            print("  Typed prompt")
        else:
            print("  ERROR: No editor found")
            return
        
        await asyncio.sleep(1)
        await page.screenshot(path=str(OUTPUT_DIR / "01_before_submit.png"))
        
        # Submit
        submit = await page.query_selector('button[aria-label*="Send"], button[aria-label*="Absenden"]')
        if not submit:
            # Find by data-testid or other attributes
            buttons = await page.query_selector_all('button')
            for btn in buttons:
                aria = await btn.get_attribute('aria-label') or ''
                text = await btn.inner_text() or ''
                if 'send' in aria.lower() or 'absenden' in text.lower():
                    submit = btn
                    break
        
        if submit:
            disabled = await submit.get_attribute('disabled')
            if not disabled:
                await submit.click()
                print("  Submitted!")
            else:
                print("  Submit disabled, pressing Ctrl+Enter...")
                await page.keyboard.press('Control+Enter')
        else:
            print("  No submit button, pressing Ctrl+Enter...")
            await page.keyboard.press('Control+Enter')
        
        # Wait for generation
        print("  Waiting for Grok to generate (this may take 30-60s)...")
        start = time.time()
        last_screenshot = 0
        generated = False
        
        for i in range(120):  # 2 min max
            await asyncio.sleep(2)
            
            # Check for generated images or completion indicators
            # Look for image elements that appeared after submission
            download_btns = await page.query_selector_all('button:has-text("Download")')
            copy_btns = await page.query_selector_all('button:has-text("Kopieren")')
            
            # Check if response is complete (multiple copy buttons = response done)
            if len(copy_btns) >= 2 and time.time() - start > 10:
                print(f"\n  Response complete after {time.time()-start:.0f}s")
                generated = True
                break
            
            # Progress indicator
            if i % 5 == 0:
                elapsed = time.time() - start
                print(f"  ... {elapsed:.0f}s elapsed")
                # Take periodic screenshots
                await page.screenshot(path=str(OUTPUT_DIR / f"02_progress_{i}.png"))
        
        if generated or time.time() - start > 30:
            # Take final screenshot
            await asyncio.sleep(3)
            await page.screenshot(path=str(OUTPUT_DIR / "03_final_result.png"), full_page=True)
            print(f"  Saved final result screenshot")
            
            # Try to find and download generated images
            imgs = await page.query_selector_all('img')
            img_count = 0
            for img in imgs:
                src = await img.get_attribute('src') or ''
                alt = await img.get_attribute('alt') or ''
                if ('blob:' in src or 'generated' in alt.lower() or 
                    'grok' in src.lower() or src.startswith('https://assets')):
                    # Try to download this image
                    try:
                        bbox = await img.bounding_box()
                        if bbox and bbox['width'] > 200 and bbox['height'] > 200:
                            img_count += 1
                            # Right-click and save, or evaluate to get src
                            img_src = await page.evaluate('(el) => el.src', img)
                            print(f"  Found large image: {img_src[:100]}...")
                    except:
                        pass
            
            # Click download if available
            dl_btns = await page.query_selector_all('button:has-text("Download")')
            for idx, btn in enumerate(dl_btns):
                try:
                    async with page.expect_download(timeout=10000) as dl_info:
                        await btn.click()
                    download = await dl_info.value
                    out_path = OUTPUT_DIR / f"generated_{idx}.png"
                    await download.save_as(str(out_path))
                    print(f"  Downloaded: {out_path}")
                except Exception as e:
                    print(f"  Download {idx} failed: {e}")
            
            print(f"\n  All done! Check {OUTPUT_DIR}")
        else:
            print("  Timed out waiting for generation")
            await page.screenshot(path=str(OUTPUT_DIR / "03_timeout.png"), full_page=True)

if __name__ == "__main__":
    asyncio.run(main())
