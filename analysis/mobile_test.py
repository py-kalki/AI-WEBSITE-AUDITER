import asyncio
from playwright.async_api import async_playwright

class MobileTest:
    async def check(self, url):
        """Checks if the website is mobile responsive."""
        if not url.startswith('http'):
            url = 'http://' + url
            
        score = 100
        issues = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            # Emulate a mobile device (iPhone 12)
            device = p.devices['iPhone 12']
            context = await browser.new_context(**device)
            page = await context.new_page()
            
            try:
                await page.goto(url, timeout=30000)
                
                # Check for horizontal scroll (common mobile issue)
                scroll_width = await page.evaluate("document.body.scrollWidth")
                viewport_width = await page.evaluate("window.innerWidth")
                
                if scroll_width > viewport_width:
                    score -= 30
                    issues.append("Horizontal scroll detected (content overflows screen)")
                
                # Check if text is readable without zooming (heuristic)
                # This is complex to do perfectly, but we can check for meta viewport again or computed styles
                viewport_meta = await page.query_selector('meta[name="viewport"]')
                if not viewport_meta:
                    # Already checked in UX, but good to double check in context
                    pass
                    
            except Exception as e:
                print(f"Error checking mobile responsiveness for {url}: {e}")
                score = 0
                issues.append("Failed to load on mobile emulator")
            finally:
                await browser.close()
                
        return {
            "score": score,
            "issues": issues
        }

if __name__ == "__main__":
    tester = MobileTest()
    print(asyncio.run(tester.check("example.com")))
