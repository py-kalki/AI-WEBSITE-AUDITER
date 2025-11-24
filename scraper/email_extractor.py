import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
from config import USER_AGENT

class EmailExtractor:
    def __init__(self):
        self.headers = {"User-Agent": USER_AGENT}
        self.email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        
    def extract(self, url):
        """Extracts email from the given URL."""
        if not url:
            return None
            
        if not url.startswith('http'):
            url = 'http://' + url
            
        print(f"Extracting email from: {url}")
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                return None
                
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text()
            
            # Find all emails
            emails = re.findall(self.email_regex, text)
            
            # Filter out common false positives (like image extensions or example.com)
            valid_emails = [e for e in emails if not e.endswith(('.png', '.jpg', '.jpeg', '.gif', 'example.com'))]
            
            if valid_emails:
                return valid_emails[0] # Return the first one found
            
            # If not found in text, check mailto links
            mailto_links = soup.select('a[href^="mailto:"]')
            for link in mailto_links:
                href = link.get('href')
                if href:
                    email = href.replace('mailto:', '').split('?')[0]
                    if re.match(self.email_regex, email):
                        return email
                        
            return None
            
        except Exception as e:
            print(f"Error extracting email from {url}: {e}")
            return None

if __name__ == "__main__":
    extractor = EmailExtractor()
    print(extractor.extract("https://www.example.com"))
