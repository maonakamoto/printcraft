#!/usr/bin/env python3
"""Download generated images from all open Grok tabs in Brave."""

import asyncio
import base64
import os
import re
from playwright.async_api import async_playwright

CDP_URL = "http://127.0.0.1:9333"
OUTPUT_DIR = "/home/g/Dokumente/Duschwand/7photos-edited"

SCENE_NAMES = [
    "grok_1_hero_v2",
    "grok_2_white_v2",
    "grok_4_blue_v2",
    "grok_5_hydrofoil_v2",
    "grok_6_jetranger_v2",
    "grok_7_vv_van_v2",
]

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(CDP_URL)
        contexts = browser.contexts
        if not contexts:
            print("No browser context found!")
            return
        
        context = contexts[0]
        pages = context.pages
        print(f"Found {len(pages)} open pages")
        
        grok_pages = [pg for pg in pages if 'grok.com' in pg.url and not pg.url.startswith('blob:')]
        print(f"Found {len(grok_pages)} Grok pages")
        
        scene_idx = 0
        for pg in grok_pages:
            url = pg.url
            print(f"\nPage: {url[:80]}")
            
            # Find all generated images
            imgs = await pg.query_selector_all('img')
            gen_imgs = []
            for img in imgs:
                src = await img.get_attribute('src') or ''
                if 'assets.grok.com' in src and '/generated/' in src:
                    gen_imgs.append((img, src))
            
            if not gen_imgs:
                print("  No generated images found")
                continue
            
            print(f"  Found {len(gen_imgs)} generated image(s)")
            
            for i, (img, src) in enumerate(gen_imgs):
                # Try downloading via page fetch with credentials
                try:
                    img_data = await pg.evaluate("""
                        async (url) => {
                            try {
                                const resp = await fetch(url, { credentials: 'include' });
                                if (!resp.ok) return { error: resp.status };
                                const blob = await resp.blob();
                                return new Promise((resolve) => {
                                    const reader = new FileReader();
                                    reader.onloadend = () => resolve({ data: reader.result });
                                    reader.readAsDataURL(blob);
                                });
                            } catch(e) {
                                return { error: e.message };
                            }
                        }
                    """, src)
                    
                    if 'error' in img_data:
                        print(f"  Fetch failed ({img_data['error']}), trying screenshot method...")
                        # Fallback: screenshot the image element
                        box = await img.bounding_box()
                        if box and box['width'] > 100:
                            if scene_idx < len(SCENE_NAMES):
                                name = SCENE_NAMES[scene_idx]
                            else:
                                name = f"unknown_{scene_idx}"
                            suffix = f"_alt" if i > 0 else ""
                            path = f"{OUTPUT_DIR}/{name}{suffix}_screenshot.png"
                            await img.screenshot(path=path)
                            size = os.path.getsize(path)
                            print(f"  Screenshot saved: {path} ({size//1024}KB)")
                    elif 'data' in img_data and img_data['data']:
                        data = img_data['data']
                        if data.startswith('data:'):
                            b64 = data.split(',', 1)[1]
                            img_bytes = base64.b64decode(b64)
                            if scene_idx < len(SCENE_NAMES):
                                name = SCENE_NAMES[scene_idx]
                            else:
                                name = f"unknown_{scene_idx}"
                            suffix = f"_alt" if i > 0 else ""
                            path = f"{OUTPUT_DIR}/{name}{suffix}.png"
                            with open(path, 'wb') as f:
                                f.write(img_bytes)
                            print(f"  SAVED: {path} ({len(img_bytes)//1024}KB)")
                except Exception as e:
                    print(f"  Error: {e}")
                    # Last resort: screenshot
                    try:
                        if scene_idx < len(SCENE_NAMES):
                            name = SCENE_NAMES[scene_idx]
                        else:
                            name = f"unknown_{scene_idx}"
                        suffix = f"_alt" if i > 0 else ""
                        path = f"{OUTPUT_DIR}/{name}{suffix}_screenshot.png"
                        await img.screenshot(path=path)
                        size = os.path.getsize(path)
                        print(f"  Screenshot fallback: {path} ({size//1024}KB)")
                    except Exception as e2:
                        print(f"  Screenshot also failed: {e2}")
            
            if gen_imgs:
                scene_idx += 1

        print(f"\nDone! Processed {scene_idx} scenes")

asyncio.run(main())
