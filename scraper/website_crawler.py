import requests
from bs4 import BeautifulSoup
from config import USER_AGENT

class WebsiteCrawler:
    def __init__(self):
        self.headers = {"User-Agent": USER_AGENT}

    def validate_website(self, url):
        """Checks if the website is accessible and returns the HTML content."""
        if not url.startswith('http'):
            url = 'http://' + url
            
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return True, response.text, response.url
            else:
                return False, None, url
        except Exception as e:
            print(f"Error crawling {url}: {e}")
            return False, None, url

    def extract_content(self, html):
        """Extracts text content and internal links."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        text = soup.get_text()
        
        # Break into lines and remove leading/trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        links = [a['href'] for a in soup.find_all('a', href=True)]
        
        return text, links

if __name__ == "__main__":
    crawler = WebsiteCrawler()
    valid, html, final_url = crawler.validate_website("example.com")
    if valid:
        print(f"Successfully crawled {final_url}")
        text, links = crawler.extract_content(html)
        print(f"Extracted {len(text)} characters and {len(links)} links.")
    else:
        print("Failed to crawl.")
