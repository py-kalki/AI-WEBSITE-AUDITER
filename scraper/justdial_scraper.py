import requests
from bs4 import BeautifulSoup
from config import USER_AGENT

class JustDialScraper:
    def __init__(self):
        self.base_url = "https://www.justdial.com"
        self.headers = {"User-Agent": USER_AGENT}

    def scrape(self, keyword, location, total=10):
        """Scrapes JustDial for businesses."""
        # JustDial URL structure: https://www.justdial.com/{location}/{keyword}
        url = f"{self.base_url}/{location}/{keyword}"
        print(f"Scraping JustDial: {url}")
        
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code != 200:
                print(f"Failed to fetch JustDial page: {response.status_code}")
                return []
            
            return self.parse_html(response.text, total)
        except Exception as e:
            print(f"Error scraping JustDial: {e}")
            return []

    def parse_html(self, html, total):
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        # Selectors for JustDial (subject to change)
        # Looking for result cards
        cards = soup.select('.resultbox') 
        
        for card in cards[:total]:
            try:
                name_el = card.select_one('.resultbox_title_anchor')
                name = name_el.text.strip() if name_el else "Unknown"
                
                # Phone numbers are often obfuscated or require clicking.
                # Sometimes present in class 'contact-info'
                phone_el = card.select_one('.contact-info')
                phone = phone_el.text.strip() if phone_el else "N/A"
                
                address_el = card.select_one('.address-info')
                address = address_el.text.strip() if address_el else "N/A"
                
                website_el = card.select_one('.website_icon')
                website = website_el['href'] if website_el else None
                
                business = {
                    "business_name": name,
                    "category": "N/A",
                    "address": address,
                    "phone": phone,
                    "website": website,
                    "source": "JustDial"
                }
                results.append(business)
            except Exception as e:
                continue
                
        return results

if __name__ == "__main__":
    scraper = JustDialScraper()
    # Note: JustDial scraping often requires specific location formatting or might block requests.
    # This is a basic implementation.
    results = scraper.scrape("Dentist", "Mumbai", total=5)
    print(results)
