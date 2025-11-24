from bs4 import BeautifulSoup
import requests
from config import USER_AGENT

class SEOAnalyzer:
    def __init__(self):
        self.headers = {"User-Agent": USER_AGENT}

    def analyze(self, url, html_content=None):
        """Analyzes SEO factors of a website."""
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
        
        # Title Check
        title = soup.title.string if soup.title else None
        if not title:
            score -= 20
            issues.append("Missing <title> tag")
        elif len(title) < 10 or len(title) > 60:
            score -= 5
            issues.append("Title length should be between 10-60 characters")
            
        # Meta Description Check
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if not meta_desc or not meta_desc.get('content'):
            score -= 20
            issues.append("Missing meta description")
        
        # H1 Check
        h1s = soup.find_all('h1')
        if not h1s:
            score -= 20
            issues.append("Missing <h1> tag")
        elif len(h1s) > 1:
            score -= 5
            issues.append("Multiple <h1> tags found (should be one)")
            
        # Image Alt Text Check
        images = soup.find_all('img')
        missing_alt = [img for img in images if not img.get('alt')]
        if missing_alt:
            penalty = min(20, len(missing_alt) * 2)
            score -= penalty
            issues.append(f"{len(missing_alt)} images missing alt text")
            
        return {
            "score": max(0, int(score)),
            "issues": issues
        }

if __name__ == "__main__":
    analyzer = SEOAnalyzer()
    print(analyzer.analyze("example.com"))
