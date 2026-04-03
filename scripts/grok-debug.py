#!/usr/bin/env python3
"""Debug Grok UI to find the right selectors."""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9223")
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
        
        # Print all buttons and menuitems
        print("=== BUTTONS ===")
        buttons = await page.query_selector_all('button')
        for btn in buttons:
            text = (await btn.inner_text()).strip()[:80]
            aria = await btn.get_attribute('aria-label') or ''
            if text or aria:
                print(f"  btn: text='{text}' aria='{aria}'")
        
        print("\n=== ATTACH MENU ===")
        # Click attach button
        attach = await page.query_selector('button[aria-label*="Anhäng"], button[aria-label*="Attach"]')
        if not attach:
            # Find by icon/position - it's near the text input
            for btn in buttons:
                aria = await btn.get_attribute('aria-label') or ''
                text = (await btn.inner_text()).strip()
                if 'anhäng' in aria.lower() or 'attach' in aria.lower() or 'anhäng' in text.lower():
                    attach = btn
                    break
        
        if attach:
            print(f"  Found attach button")
            await attach.click()
            await asyncio.sleep(1)
            
            # Print menu items
            menuitems = await page.query_selector_all('[role="menuitem"]')
            for item in menuitems:
                text = (await item.inner_text()).strip()[:100]
                print(f"  menuitem: '{text}'")
            
            # Also check for any popup/dropdown
            all_text = await page.query_selector_all('li, [role="option"], [role="menuitem"], .dropdown-item')
            for el in all_text:
                text = (await el.inner_text()).strip()[:100]
                tag = await el.evaluate('el => el.tagName')
                role = await el.get_attribute('role') or ''
                print(f"  {tag}[{role}]: '{text}'")
        
        # Also check for hidden file inputs
        print("\n=== FILE INPUTS ===")
        inputs = await page.query_selector_all('input[type="file"]')
        print(f"  Found {len(inputs)} file input(s)")
        for inp in inputs:
            accept = await inp.get_attribute('accept') or ''
            multiple = await inp.get_attribute('multiple')
            print(f"  accept='{accept}' multiple={multiple}")
        
        await page.screenshot(path="/home/g/dev/printcraft/projects/duschwand-roli/generated/round1-grok/debug.png")
        print("\nSaved debug screenshot")

asyncio.run(main())
