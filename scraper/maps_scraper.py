import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import time
import random

from scraper.email_extractor import EmailExtractor

class MapsScraper:
    def __init__(self):
        self.results = []
        self.email_extractor = EmailExtractor()

    async def scrape(self, keyword, location, total=10):
        """Scrapes Google Maps for businesses."""
        search_term = f"{keyword} in {location}"
        print(f"Scraping Maps for: {search_term}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            await page.goto("https://www.google.com/maps", timeout=60000)
            await page.wait_for_selector("input#searchboxinput")
            
            await page.fill("input#searchboxinput", search_term)
            await page.keyboard.press("Enter")
            
            # Wait for results to load
            try:
                await page.wait_for_selector('div[role="feed"]', timeout=10000)
            except:
                print("Could not find results feed. Trying to find single result...")
                pass

            # Scroll to load more results
            feed_selector = 'div[role="feed"]'
            for _ in range(3): # Scroll a few times
                try:
                    await page.hover(feed_selector)
                    await page.mouse.wheel(0, 5000)
                    await asyncio.sleep(2)
                except:
                    pass
            
            # Extract items
            items = await page.query_selector_all('div[role="article"]')
            print(f"Found {len(items)} potential items. Processing top {total}...")
            
            count = 0
            for item in items:
                if count >= total:
                    break
                
                try:
                    # Get name from aria-label BEFORE clicking (more reliable)
                    name = await item.get_attribute('aria-label')
                    if not name:
                        continue

                    # Click the item to load details
                    await item.click()
                    await asyncio.sleep(2) # Wait for detail panel to load
                    
                    # Website
                    # Look for a link with data-item-id="authority" or similar
                    website_el = await page.query_selector('a[data-item-id="authority"]')
                    website = await website_el.get_attribute('href') if website_el else None
                    
                    # If no website, skip
                    if not website:
                        print(f"Skipping {name} (No website)")
                        continue
                        
                    # Phone
                    phone_el = await page.query_selector('button[data-item-id^="phone"]')
                    phone = await phone_el.get_attribute('aria-label') if phone_el else None
                    if phone:
                        phone = phone.replace("Phone: ", "").strip()
                    
                    # Address
                    address_el = await page.query_selector('button[data-item-id="address"]')
                    address = await address_el.get_attribute('aria-label') if address_el else None
                    if address:
                        address = address.replace("Address: ", "").strip()
                        
                    # Email Extraction (New)
                    email = self.email_extractor.extract(website)

                    business = {
                        "business_name": name,
                        "category": keyword,
                        "address": address or "N/A",
                        "phone": phone or "N/A",
                        "email": email or "N/A",
                        "website": website,
                        "source": "Google Maps"
                    }
                    
                    self.results.append(business)
                    print(f"Extracted: {name} - {website} - {email}")
                    count += 1
                    
                except Exception as e:
                    print(f"Error processing item: {e}")
                    continue
            
            await browser.close()
        
        return self.results

    def parse_html(self, html, keyword):
        # Legacy method, not used in new logic but kept for interface compatibility if needed
        pass

if __name__ == "__main__":
    scraper = MapsScraper()
    results = asyncio.run(scraper.scrape("Dentist", "New York", total=3))
    print(results)
