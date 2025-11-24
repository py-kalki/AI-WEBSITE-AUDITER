import requests
import time
from config import USER_AGENT

class PerformanceAnalyzer:
    def __init__(self):
        self.headers = {"User-Agent": USER_AGENT}

    def analyze(self, url):
        """Analyzes the performance of a website."""
        if not url.startswith('http'):
            url = 'http://' + url
            
        start_time = time.time()
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            end_time = time.time()
            
            response_time = end_time - start_time
            page_size_kb = len(response.content) / 1024
            
            score = self.calculate_score(response_time, page_size_kb)
            
            return {
                "response_time_seconds": round(response_time, 2),
                "page_size_kb": round(page_size_kb, 2),
                "score": score
            }
        except Exception as e:
            print(f"Error analyzing performance for {url}: {e}")
            return {
                "response_time_seconds": -1,
                "page_size_kb": -1,
                "score": 0
            }

    def calculate_score(self, response_time, page_size_kb):
        # Basic scoring logic
        score = 100
        
        # Deduct for slow response
        if response_time > 1.0:
            score -= (response_time - 1.0) * 20
        
        # Deduct for large page size (e.g., > 2MB)
        if page_size_kb > 2000:
            score -= (page_size_kb - 2000) / 100
            
        return max(0, min(100, int(score)))

if __name__ == "__main__":
    analyzer = PerformanceAnalyzer()
    print(analyzer.analyze("example.com"))
