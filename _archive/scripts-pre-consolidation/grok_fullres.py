#!/usr/bin/env python3
"""Download full-res images from assets.grok.com via authenticated Brave session."""

import asyncio
import base64
from playwright.async_api import async_playwright

CDP_URL = "http://127.0.0.1:9333"
OUT = "/home/g/Dokumente/Duschwand/7photos-edited"

IMAGES = {
    "grok_1_hero_v2": "https://assets.grok.com/users/c3e7f8ab-e566-43a6-8f79-4ede77a11efd/generated/586edeb2-96ed-4c9b-ae69-15fb88d37205/image.jpg",
    "grok_2_white_v2": "https://assets.grok.com/users/c3e7f8ab-e566-43a6-8f79-4ede77a11efd/generated/63052d5e-b8f0-46b2-bc92-b97728599687/image.jpg",
    "grok_4_blue_v2": "https://assets.grok.com/users/c3e7f8ab-e566-43a6-8f79-4ede77a11efd/generated/7be6bd02-9cf3-4181-b719-2a773f7f00ae/image.jpg",
    "grok_5_hydrofoil_v2": "https://assets.grok.com/users/c3e7f8ab-e566-43a6-8f79-4ede77a11efd/generated/950fd17f-27b8-4740-8c91-7c3f4947e8ae/image.jpg",
    "grok_6_jetranger_v2": "https://assets.grok.com/users/c3e7f8ab-e566-43a6-8f79-4ede77a11efd/generated/2028d7d3-b9c2-4ec8-a743-ebf463187fa9/image.jpg",
    "grok_7_vv_van_v2": "https://assets.grok.com/users/c3e7f8ab-e566-43a6-8f79-4ede77a11efd/generated/04374782-7c43-458c-888a-755ba600cf86/image.jpg",
}

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(CDP_URL)
        context = browser.contexts[0]
        
        # First, go to grok.com to have proper cookies
        page = await context.new_page()
        await page.goto("https://grok.com/", wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)
        
        for name, url in IMAGES.items():
            print(f"\nDownloading {name}...")
            try:
                # Use page.evaluate to fetch with cookies
                result = await page.evaluate(f"""
                    async () => {{
                        try {{
                            const resp = await fetch('{url}', {{ 
                                credentials: 'include',
                                headers: {{ 'Accept': 'image/*' }}
                            }});
                            if (!resp.ok) {{
                                return {{ error: resp.status + ' ' + resp.statusText }};
                            }}
                            const blob = await resp.blob();
                            const reader = new FileReader();
                            return new Promise(resolve => {{
                                reader.onloadend = () => resolve({{ 
                                    data: reader.result, 
                                    type: blob.type, 
                                    size: blob.size 
                                }});
                                reader.readAsDataURL(blob);
                            }});
                        }} catch(e) {{
                            return {{ error: e.message }};
                        }}
                    }}
                """)
                
                if 'error' in result:
                    print(f"  Error: {result['error']}")
                    
                    # Try opening the URL directly as a page
                    print(f"  Trying direct navigation...")
                    img_page = await context.new_page()
                    resp = await img_page.goto(url, timeout=15000)
                    if resp and resp.ok:
                        # Screenshot the page (which should just be the image)
                        await asyncio.sleep(2)
                        await img_page.screenshot(path=f"{OUT}/{name}_fullres.png")
                        import os
                        size = os.path.getsize(f"{OUT}/{name}_fullres.png")
                        print(f"  Page screenshot: {size//1024}KB")
                    else:
                        print(f"  Navigation failed: {resp.status if resp else 'no response'}")
                    await img_page.close()
                else:
                    data = result.get('data', '')
                    blob_size = result.get('size', 0)
                    if data.startswith('data:'):
                        b64 = data.split(',', 1)[1]
                        img_bytes = base64.b64decode(b64)
                        ext = 'jpg' if 'jpeg' in result.get('type', '') else 'png'
                        path = f"{OUT}/{name}_fullres.{ext}"
                        with open(path, 'wb') as f:
                            f.write(img_bytes)
                        print(f"  SAVED: {path} ({len(img_bytes)//1024}KB, blob was {blob_size//1024}KB)")
                    else:
                        print(f"  Empty data response")
            except Exception as e:
                print(f"  Exception: {e}")
        
        await page.close()
        print("\nDone!")

asyncio.run(main())
