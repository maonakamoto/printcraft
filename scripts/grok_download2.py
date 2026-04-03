#!/usr/bin/env python3
"""Re-open recent Grok conversations and download the generated images."""

import asyncio
import base64
import os
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

async def download_img(page, img_el, path):
    """Try fetch, then screenshot fallback."""
    src = await img_el.get_attribute('src') or ''
    
    # Method 1: fetch with credentials
    try:
        result = await page.evaluate("""
            async (url) => {
                const resp = await fetch(url, { credentials: 'include' });
                if (!resp.ok) return null;
                const blob = await resp.blob();
                return new Promise(r => {
                    const reader = new FileReader();
                    reader.onloadend = () => r(reader.result);
                    reader.readAsDataURL(blob);
                });
            }
        """, src)
        if result and result.startswith('data:'):
            b64 = result.split(',', 1)[1]
            data = base64.b64decode(b64)
            if len(data) > 1000:
                with open(path, 'wb') as f:
                    f.write(data)
                print(f"  Downloaded: {path} ({len(data)//1024}KB)")
                return True
    except:
        pass
    
    # Method 2: element screenshot
    try:
        await img_el.screenshot(path=path)
        size = os.path.getsize(path)
        if size > 1000:
            print(f"  Screenshot: {path} ({size//1024}KB)")
            return True
    except:
        pass
    
    # Method 3: right-click save via CDP (direct image URL fetch)
    try:
        # Use page.request to fetch the image
        response = await page.request.get(src)
        if response.ok:
            data = await response.body()
            with open(path, 'wb') as f:
                f.write(data)
            print(f"  API fetch: {path} ({len(data)//1024}KB)")
            return True
    except:
        pass
    
    print(f"  FAILED to download: {src[:80]}")
    return False


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(CDP_URL)
        context = browser.contexts[0]
        
        # Open grok.com
        page = await context.new_page()
        await page.goto("https://grok.com/", wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(8)
        
        # Take screenshot to see current state
        await page.screenshot(path=f"{OUTPUT_DIR}/debug_download_1.png")
        
        # Look for conversation history in sidebar
        # Grok typically has a sidebar with recent conversations
        sidebar_items = await page.query_selector_all('a[href*="/chat/"], nav a, aside a, [class*="conversation"], [class*="history"]')
        print(f"Found {len(sidebar_items)} sidebar items")
        
        for item in sidebar_items[:10]:
            text = await item.text_content() or ''
            href = await item.get_attribute('href') or ''
            print(f"  {text[:50]} -> {href[:80]}")
        
        # Alternative: Check all links on page
        all_links = await page.query_selector_all('a')
        chat_links = []
        for link in all_links:
            href = await link.get_attribute('href') or ''
            if '/chat/' in href:
                text = await link.text_content() or ''
                chat_links.append((href, text.strip()[:60]))
        
        print(f"\nFound {len(chat_links)} chat links:")
        for href, text in chat_links:
            print(f"  {text} -> {href}")
        
        # Visit each recent conversation and look for generated images
        scene_idx = 0
        visited = set()
        for href, text in chat_links:
            if href in visited or scene_idx >= len(SCENE_NAMES):
                continue
            visited.add(href)
            
            full_url = f"https://grok.com{href}" if href.startswith('/') else href
            print(f"\nVisiting: {full_url}")
            await page.goto(full_url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(5)
            
            # Find generated images
            imgs = await page.query_selector_all('img')
            gen_imgs = []
            for img in imgs:
                src = await img.get_attribute('src') or ''
                if 'assets.grok.com' in src and '/generated/' in src:
                    box = await img.bounding_box()
                    gen_imgs.append((img, src, box))
            
            if gen_imgs:
                print(f"  Found {len(gen_imgs)} generated image(s)")
                name = SCENE_NAMES[scene_idx]
                for i, (img, src, box) in enumerate(gen_imgs):
                    suffix = f"_alt" if i > 0 else ""
                    path = f"{OUTPUT_DIR}/{name}{suffix}.png"
                    await download_img(page, img, path)
                scene_idx += 1
            else:
                print("  No generated images")
        
        # If no chat links found, dump page HTML for debugging
        if not chat_links:
            html = await page.content()
            with open(f"{OUTPUT_DIR}/debug_grok_page.html", 'w') as f:
                f.write(html)
            print("Saved page HTML for debugging")
        
        await page.close()
        print(f"\nProcessed {scene_idx} conversations")

asyncio.run(main())
