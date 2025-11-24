from bs4 import BeautifulSoup
import requests
from config import USER_AGENT

class UXAnalyzer:
    def __init__(self):
        self.headers = {"User-Agent": USER_AGENT}

    def analyze(self, url, html_content=None):
        """Analyzes basic UX factors."""
        # Note: Real UX analysis requires rendering (Playwright/Selenium) to check computed styles.
        # This is a static analysis approximation.
        
        if not html_content:
            if not url.startswith('http'):
                url = 'http://' + url
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                html_content = response.text
            except:
                return {"score": 0, "issues": ["Could not fetch website"]}

        soup = BeautifulSoup(html_content, 'html.parser')
        issues = []
        score = 100
        
        # Check for viewport meta tag (crucial for mobile UX)
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        if not viewport:
            score -= 30
            issues.append("Missing viewport meta tag (not mobile friendly)")
            
        # Check for too many links (cluttered navigation)
        links = soup.find_all('a')
        if len(links) > 100:
            score -= 10
            issues.append("Too many links on page (potential clutter)")
            
        # Check for very small paragraphs (readability)
        # This is a heuristic
        paragraphs = soup.find_all('p')
        short_paragraphs = [p for p in paragraphs if len(p.get_text()) < 20]
        if len(short_paragraphs) > 5:
            score -= 5
            issues.append("Many short paragraphs detected (content might be thin)")

        return {
            "score": max(0, int(score)),
            "issues": issues
        }

if __name__ == "__main__":
    analyzer = UXAnalyzer()
    print(analyzer.analyze("example.com"))
