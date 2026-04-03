#!/usr/bin/env python3
"""Generate cartoon characters via Grok Imagine using CDP connection to user's Chrome."""

import asyncio
import sys
import os
import time
import base64
from pathlib import Path
from playwright.async_api import async_playwright

CDP_URL = "http://127.0.0.1:9223"
OUTPUT_DIR = Path("/home/g/dev/printcraft/projects/duschwand-roli/generated/round1-grok")
REFS_DIR = Path("/home/g/Dokumente/Duschwand")


async def wait_for_images(page, timeout=120):
    """Wait for generated images to appear."""
    start = time.time()
    while time.time() - start < timeout:
        # Look for generated image containers or download buttons
        imgs = await page.query_selector_all('img[src*="imagine"], img[src*="generated"], img[alt*="Generated"]')
        download_btns = await page.query_selector_all('button:has-text("Download"), button:has-text("Herunterladen")')
        save_btns = await page.query_selector_all('button:has-text("Speichern")')
        
        if download_btns:
            print(f"  Found download button after {time.time()-start:.0f}s")
            return "download"
        
        # Check for new images in the page
        all_imgs = await page.query_selector_all('img')
        for img in all_imgs:
            src = await img.get_attribute('src') or ''
            if 'blob:' in src or 'imagine' in src or 'generated' in src:
                print(f"  Found generated image after {time.time()-start:.0f}s")
                return "image"
        
        await asyncio.sleep(3)
        sys.stdout.write('.')
        sys.stdout.flush()
    
    return None


async def generate_character(page, name, ref_file, prompt):
    """Generate a single character via Grok Imagine with image upload."""
    print(f"\n{'='*60}")
    print(f"Generating: {name}")
    print(f"{'='*60}")

    # Navigate fresh
    await page.goto("https://grok.com/imagine", wait_until="networkidle", timeout=30000)
    await asyncio.sleep(3)

    # Set 1:1 aspect ratio
    ratio_btn = await page.query_selector('button:has-text("2:3")')
    if ratio_btn:
        await ratio_btn.click()
        await asyncio.sleep(0.5)
        sq = await page.query_selector('[role="menuitem"]:has-text("1:1")')
        if sq:
            await sq.click()
            print("  Set 1:1 aspect ratio")
            await asyncio.sleep(0.5)

    # Upload via input[type=file] — set files directly on hidden file input
    # First, try to find any file input on the page
    file_inputs = await page.query_selector_all('input[type="file"]')
    
    if file_inputs:
        print(f"  Found {len(file_inputs)} file input(s), uploading directly...")
        await file_inputs[0].set_input_files(str(ref_file))
        await asyncio.sleep(3)
    else:
        # Create a file input and inject the file via JavaScript
        print("  No file input found. Using attach button with file chooser...")
        
        # Arm file chooser BEFORE triggering the dialog
        attach_btn = await page.query_selector('button[aria-label*="Anhängen"], button[aria-label*="Attach"]')
        if not attach_btn:
            attach_btn = await page.query_selector('button:has-text("Anhängen")')
        
        if attach_btn:
            # Use expect_file_chooser with the full click sequence
            try:
                async with page.expect_file_chooser(timeout=10000) as fc_info:
                    await attach_btn.click()
                    await asyncio.sleep(1)
                    # Click "Bilder bearbeiten"
                    edit_opt = await page.query_selector('[role="menuitem"]:has-text("Bilder bearbeiten"), [role="menuitem"]:has-text("Edit images")')
                    if edit_opt:
                        await edit_opt.click()
                
                file_chooser = await fc_info.value
                await file_chooser.set_files(str(ref_file))
                print(f"  Uploaded via file chooser: {ref_file.name}")
                await asyncio.sleep(3)
            except Exception as e:
                print(f"  File chooser failed: {e}")
                print("  Trying drag-and-drop approach...")
                
                # Read file as base64 and inject via JS drag-and-drop simulation
                with open(ref_file, 'rb') as f:
                    b64 = base64.b64encode(f.read()).decode()
                
                await page.evaluate(f"""
                    async () => {{
                        const b64 = "{b64}";
                        const byteChars = atob(b64);
                        const byteNumbers = new Array(byteChars.length);
                        for (let i = 0; i < byteChars.length; i++) {{
                            byteNumbers[i] = byteChars.charCodeAt(i);
                        }}
                        const byteArray = new Uint8Array(byteNumbers);
                        const blob = new Blob([byteArray], {{type: 'image/png'}});
                        const file = new File([blob], "{ref_file.name}", {{type: 'image/png'}});
                        
                        const dt = new DataTransfer();
                        dt.items.add(file);
                        
                        const dropZone = document.querySelector('[contenteditable]') || document.body;
                        const dropEvent = new DragEvent('drop', {{
                            bubbles: true,
                            cancelable: true,
                            dataTransfer: dt
                        }});
                        dropZone.dispatchEvent(dropEvent);
                    }}
                """)
                print("  Attempted drag-and-drop upload")
                await asyncio.sleep(3)

    # Check if image was attached
    remove_btn = await page.query_selector('button:has-text("Remove"), button[aria-label*="Remove"]')
    img_preview = await page.query_selector('button:has-text("Weitere Bilder"), button:has-text("Add more")')
    if remove_btn or img_preview:
        print("  Image attached successfully!")
    else:
        print("  WARNING: Image may not have attached. Continuing with text-only prompt...")

    # Type the prompt
    editor = await page.query_selector('[contenteditable]')
    if not editor:
        editor = await page.query_selector('textarea')
    
    if editor:
        await editor.click()
        await asyncio.sleep(0.5)
        await editor.type(prompt, delay=10)
        print(f"  Typed prompt")
    else:
        print("  ERROR: No editor found!")
        return None

    await asyncio.sleep(1)

    # Submit
    submit = await page.query_selector('button[aria-label*="Absenden"], button[aria-label*="Submit"], button:has-text("Absenden")')
    if submit:
        disabled = await submit.get_attribute('disabled')
        if disabled:
            print("  Submit button disabled, pressing Enter instead...")
            await editor.press('Enter')
        else:
            await submit.click()
    else:
        await editor.press('Enter')
    
    print("  Submitted! Waiting for generation...")

    # Wait for result
    result = await wait_for_images(page)
    
    if result == "download":
        # Click download
        dl_btn = await page.query_selector('button:has-text("Download"), button:has-text("Herunterladen")')
        if dl_btn:
            async with page.expect_download(timeout=15000) as dl_info:
                await dl_btn.click()
            download = await dl_info.value
            out_path = OUTPUT_DIR / f"{name}_cartoon.png"
            await download.save_as(str(out_path))
            print(f"  SAVED: {out_path}")
            return out_path
    
    # Fallback: screenshot
    out_path = OUTPUT_DIR / f"{name}_screenshot.png"
    await page.screenshot(path=str(out_path), full_page=True)
    print(f"  Saved screenshot (fallback): {out_path}")
    return out_path


async def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    characters = {
        "Alberto": {
            "ref": REFS_DIR / "Alberto01.png",
            "prompt": "Transform @1 into a vibrant cartoon illustration. Keep his face perfectly recognizable. He is riding a jet ski on a sunny lake, having fun. Bold cartoon colors, Pixar style, sparkling blue water."
        },
        "Andreas": {
            "ref": REFS_DIR / "Andreas01.png",
            "prompt": "Transform @1 into a vibrant cartoon illustration. Keep his face perfectly recognizable. He is standing on a paddleboard on a sunny lake. Bold cartoon colors, Pixar style, sparkling blue water."
        },
        "Gela": {
            "ref": REFS_DIR / "Gela01.png",
            "prompt": "Transform @1 into a vibrant cartoon illustration. Keep her face perfectly recognizable. She is waving from a small sailboat on a sunny lake. Bold cartoon colors, Pixar style."
        },
        "Marco": {
            "ref": REFS_DIR / "Marco01.png",
            "prompt": "Transform @1 into a vibrant cartoon illustration. Keep his face perfectly recognizable. He is in an inflatable raft on a sunny lake, laughing. Bold cartoon colors, Pixar style."
        },
        "Teus": {
            "ref": REFS_DIR / "Teus01.png",
            "prompt": "Transform @1 into a vibrant cartoon illustration. Keep his face perfectly recognizable. He is water skiing on a sunny lake. Bold cartoon colors, Pixar style."
        },
        "Roma": {
            "ref": REFS_DIR / "ROMA01.png",
            "prompt": "Transform @1 into a vibrant cartoon illustration. Keep his face perfectly recognizable. He is diving off a dock into a sunny lake. Bold cartoon colors, Pixar style."
        },
    }

    targets = sys.argv[1:] if len(sys.argv) > 1 else list(characters.keys())

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(CDP_URL)
        contexts = browser.contexts
        if not contexts:
            print("ERROR: No browser contexts found")
            return
        
        context = contexts[0]
        page = None
        for pg in context.pages:
            if "grok.com" in pg.url:
                page = pg
                break
        if not page:
            page = await context.new_page()
        
        await page.goto("https://grok.com/imagine", wait_until="networkidle", timeout=30000)
        await asyncio.sleep(2)

        # Check login status
        content = await page.content()
        logged_in = "Anmelden" not in content and "Sign in" not in content
        print(f"Logged in: {logged_in}")
        
        if not logged_in:
            print("NOT LOGGED IN. Please sign in at the Chrome window on your screen.")
            print("Waiting 60s for you to log in...")
            for i in range(60):
                await asyncio.sleep(1)
                content = await page.content()
                if "Anmelden" not in content and "Sign in" not in content:
                    print("  Logged in! Continuing...")
                    logged_in = True
                    break
                if i % 10 == 0:
                    print(f"  Still waiting... ({60-i}s)")
            
            if not logged_in:
                print("Proceeding without login (limited functionality)")

        for name in targets:
            if name not in characters:
                print(f"Unknown: {name}")
                continue
            char = characters[name]
            try:
                await generate_character(page, name, char["ref"], char["prompt"])
            except Exception as e:
                print(f"  ERROR: {e}")
            await asyncio.sleep(5)

    print(f"\nDone! Results in {OUTPUT_DIR}")

if __name__ == "__main__":
    asyncio.run(main())
