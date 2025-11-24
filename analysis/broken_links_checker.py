import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from config import USER_AGENT

class BrokenLinksChecker:
    def __init__(self):
        self.headers = {"User-Agent": USER_AGENT}

    def check(self, url):
        """Checks for broken internal links."""
        if not url.startswith('http'):
            url = 'http://' + url
            
        domain = urlparse(url).netloc
        broken_links = []
        checked_links = set()
        score = 100
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a', href=True)
            
            # Limit to checking first 20 links to avoid long wait times
            links_to_check = []
            for a in links:
                href = a['href']
                full_url = urljoin(url, href)
                parsed = urlparse(full_url)
                
                if parsed.netloc == domain and full_url not in checked_links:
                    links_to_check.append(full_url)
                    checked_links.add(full_url)
            
            for link in links_to_check[:20]:
                try:
                    res = requests.head(link, headers=self.headers, timeout=5)
                    if res.status_code >= 400:
                        broken_links.append(link)
                except:
                    broken_links.append(link)
            
            if broken_links:
                penalty = min(40, len(broken_links) * 5)
                score -= penalty
                
        except Exception as e:
            print(f"Error checking links for {url}: {e}")
            return {"score": 0, "broken_links": [], "error": str(e)}

        return {
            "score": score,
            "broken_links": broken_links,
            "count": len(broken_links)
        }

if __name__ == "__main__":
    checker = BrokenLinksChecker()
    print(checker.check("example.com"))
