#!/usr/bin/env python3
"""Use SuperGrok Imagine to generate characters with face-accurate references."""
import asyncio
import sys
import time
import base64
from pathlib import Path
from playwright.async_api import async_playwright

CDP_URL = "http://127.0.0.1:9223"
REFS = Path("/home/g/Dokumente/Duschwand")
OUT = Path("/home/g/Dokumente/Duschwand/grok-generated")

async def generate(page, name, ref_files, prompt, aspect="1:1"):
    """Upload refs to Imagine, type prompt, submit, download result."""
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")
    
    await page.goto("https://grok.com/imagine", wait_until="networkidle", timeout=30000)
    await asyncio.sleep(3)
    
    # Set aspect ratio if not 2:3
    if aspect != "2:3":
        ratio_btn = await page.query_selector('button[aria-label*="Aspect"], button:has-text("2:3"), button:has-text("1:1"), button:has-text("3:2")')
        if ratio_btn:
            await ratio_btn.click()
            await asyncio.sleep(0.5)
            ar = await page.query_selector(f'[role="menuitem"]:has-text("{aspect}")')
            if ar:
                await ar.click()
                print(f"  Aspect: {aspect}")
                await asyncio.sleep(0.5)
    
    # Upload reference images via file input
    file_input = await page.query_selector('input[type="file"]')
    if file_input:
        paths = [str(f) for f in ref_files]
        await file_input.set_input_files(paths)
        print(f"  Uploaded {len(paths)} reference(s)")
        await asyncio.sleep(4)
    else:
        print("  ERROR: No file input")
        return None
    
    # Type prompt via JS insertText (avoid Enter submission)
    await page.evaluate("""(text) => {
        const el = document.querySelector('[contenteditable="true"]');
        if (el) {
            el.focus();
            document.execCommand('insertText', false, text);
        }
    }""", prompt)
    print(f"  Prompt set")
    await asyncio.sleep(1)
    
    # Submit
    submit = await page.query_selector('button[aria-label="Submit"], button[aria-label="Absenden"]')
    if submit:
        disabled = await submit.get_attribute('disabled')
        if not disabled:
            await submit.click()
            print("  Submitted!")
        else:
            print("  Submit disabled, skipping")
            return None
    else:
        print("  No submit button found")
        return None
    
    # Wait for generation (Imagine takes ~10-30s)
    print("  Generating...", end="", flush=True)
    start = time.time()
    for i in range(90):
        await asyncio.sleep(2)
        # Check for generated images
        imgs = await page.query_selector_all('img')
        for img in imgs:
            src = await img.get_attribute('src') or ''
            if 'assets.grok.com' in src and 'generated' in src:
                elapsed = time.time() - start
                print(f" done ({elapsed:.0f}s)")
                await asyncio.sleep(2)
                
                # Collect all generated image URLs
                all_imgs = await page.query_selector_all('img')
                urls = set()
                for im in all_imgs:
                    s = await im.get_attribute('src') or ''
                    if 'assets.grok.com' in s and 'generated' in s:
                        urls.add(s)
                
                # Download via cookies
                cookies = await page.context.cookies()
                cookie_str = '; '.join([f'{c["name"]}={c["value"]}' for c in cookies if 'grok' in c.get('domain','') or 'x.ai' in c.get('domain','')])
                
                downloaded = []
                for idx, url in enumerate(urls):
                    out_path = OUT / f"{name}_{idx+1}.jpg"
                    # Download in browser context
                    data = await page.evaluate(f"""async () => {{
                        try {{
                            const r = await fetch("{url}");
                            if (!r.ok) return null;
                            const blob = await r.blob();
                            const reader = new FileReader();
                            return new Promise(resolve => {{
                                reader.onloadend = () => resolve(reader.result);
                                reader.readAsDataURL(blob);
                            }});
                        }} catch(e) {{ return null; }}
                    }}""")
                    
                    if data and data.startswith('data:') and len(data) > 100:
                        b64 = data.split(',', 1)[1]
                        raw = base64.b64decode(b64)
                        out_path.write_bytes(raw)
                        downloaded.append(out_path)
                        print(f"  Saved: {out_path.name} ({len(raw)//1024}KB)")
                    else:
                        # Fallback: curl with cookies
                        import subprocess
                        subprocess.run(['curl', '-s', '-o', str(out_path), '-H', f'Cookie: {cookie_str}', url], timeout=15)
                        if out_path.stat().st_size > 1000:
                            downloaded.append(out_path)
                            print(f"  Saved (curl): {out_path.name}")
                
                return downloaded
        
        if i % 10 == 0 and i > 0:
            print(".", end="", flush=True)
    
    print(f" timeout after {time.time()-start:.0f}s")
    return None


async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    
    jobs = [
        {
            "name": "roli-gf-amphicar-main",
            "refs": [
                REFS / "real-photos/WhatsApp Image 2025-12-21 at 12.31.53.jpeg",  # Roli+gf in Amphicar
                REFS / "real-photos/WhatsApp Image 2025-12-31 at 10.14.146.jpeg",  # Amphicar group
                REFS / "ai-references/ChatGPT Image 17. März 2026, 12_12_26.png",  # Style ref
            ],
            "prompt": "Create a vibrant Pixar-style cartoon illustration with NO TEXT, NO LOGOS, NO WORDS anywhere in the image. The couple from image 1 (man driving, woman with arms spread behind him) are in a blue Amphicar amphibious car (license plate AB-N 274) driving through a sunny lake. Make their faces HIGHLY RECOGNIZABLE from the reference photo - realistic facial features in cartoon style. Around them, 6 friends ride jet skis, kayaks, sailboats, and inflatables. Bold cartoon colors, sparkling blue water, green forested hills, blue sky with fluffy clouds. Fun celebratory party-on-water atmosphere. IMPORTANT: Square 1:1 composition. No text overlays. No banners. No logos. Clean illustration only.",
            "aspect": "1:1",
        },
        {
            "name": "alberto-cartoon",
            "refs": [REFS / "ai-references/Alberto01.png"],
            "prompt": "Transform this person into a vibrant Pixar-style cartoon. Keep his face perfectly recognizable. He is riding a jet ski on a sunny lake, having fun, big smile. Bold cartoon colors, sparkling blue water.",
            "aspect": "1:1",
        },
        {
            "name": "andreas-cartoon",
            "refs": [REFS / "ai-references/Andreas01.png"],
            "prompt": "Transform this person into a vibrant Pixar-style cartoon. Keep his face perfectly recognizable. He is paddleboarding on a sunny lake, standing confidently. Bold cartoon colors, sparkling blue water.",
            "aspect": "1:1",
        },
        {
            "name": "gela-cartoon",
            "refs": [REFS / "ai-references/Gela01.png"],
            "prompt": "Transform this person into a vibrant Pixar-style cartoon. Keep her face perfectly recognizable. She is waving from a small sailboat on a sunny lake. Bold cartoon colors, sparkling blue water.",
            "aspect": "1:1",
        },
        {
            "name": "marco-cartoon",
            "refs": [REFS / "ai-references/Marco01.png"],
            "prompt": "Transform this person into a vibrant Pixar-style cartoon. Keep his face perfectly recognizable. He is lounging in an inflatable flamingo float on a sunny lake, laughing. Bold cartoon colors.",
            "aspect": "1:1",
        },
        {
            "name": "teus-cartoon",
            "refs": [REFS / "ai-references/Teus01.png"],
            "prompt": "Transform this person into a vibrant Pixar-style cartoon. Keep his face perfectly recognizable. He is water skiing on a sunny lake, action pose. Bold cartoon colors, sparkling blue water.",
            "aspect": "1:1",
        },
        {
            "name": "roma-cartoon",
            "refs": [REFS / "ai-references/ROMA01.png"],
            "prompt": "Transform this person into a vibrant Pixar-style cartoon. Keep his face perfectly recognizable. He is cannonball-diving off a wooden dock into a sunny lake. Bold cartoon colors, big splash.",
            "aspect": "1:1",
        },
    ]
    
    # Process specified jobs or all
    targets = sys.argv[1:] if len(sys.argv) > 1 else [j["name"] for j in jobs]
    
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
        
        for job in jobs:
            if job["name"] not in targets:
                continue
            try:
                result = await generate(page, job["name"], job["refs"], job["prompt"], job.get("aspect", "1:1"))
                if result:
                    print(f"  ✓ {job['name']}: {len(result)} image(s)")
                else:
                    print(f"  ✗ {job['name']}: failed")
            except Exception as e:
                print(f"  ✗ {job['name']}: {e}")
            
            # Rate limit pause between generations
            await asyncio.sleep(8)
    
    print(f"\n{'='*60}")
    print(f"All done! Check: {OUT}")
    print(f"{'='*60}")

if __name__ == "__main__":
    asyncio.run(main())
