import os
import requests
import json
from bs4 import BeautifulSoup

class AIAuditAnalyzer:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={self.api_key}"

    def analyze(self, url, html_content=None):
        """
        Analyze the website content using AI to provide a qualitative review.
        
        Args:
            url (str): The website URL.
            html_content (str, optional): Raw HTML content if already fetched.
            
        Returns:
            dict: A dictionary containing the AI review.
        """
        if not self.api_key:
            return {"error": "GEMINI_API_KEY not found."}

        # Fetch content if not provided
        if not html_content:
            try:
                response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
                if response.status_code == 200:
                    html_content = response.text
                else:
                    return {"error": f"Failed to fetch website: {response.status_code}"}
            except Exception as e:
                return {"error": f"Failed to fetch website: {str(e)}"}

        # Extract text content for the AI
        text_content = self._extract_text(html_content)
        
        # Create prompt
        prompt = self._create_prompt(url, text_content)
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 1000,
                "responseMimeType": "application/json"
            }
        }
        
        try:
            response = requests.post(self.api_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    ai_text = result['candidates'][0]['content']['parts'][0]['text'].strip()
                    # Clean up markdown code blocks if present
                    if ai_text.startswith("```json"):
                        ai_text = ai_text[7:]
                    if ai_text.endswith("```"):
                        ai_text = ai_text[:-3]
                    return json.loads(ai_text)
                else:
                    return {"error": "No AI response generated."}
            else:
                return {"error": f"AI API Error: {response.status_code} - {response.text}"}
        except Exception as e:
            return {"error": f"AI Analysis Error: {str(e)}"}

    def _extract_text(self, html):
        """Extract meaningful text from HTML."""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove scripts and styles
            for script in soup(["script", "style", "nav", "footer"]):
                script.extract()
                
            # Get text
            text = soup.get_text()
            
            # Break into lines and remove leading/trailing space on each
            lines = (line.strip() for line in text.splitlines())
            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # Drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Limit text length to avoid token limits (approx 2000 words)
            return text[:10000]
        except:
            return "Could not extract text."

    def _create_prompt(self, url, text_content):
        return f"""
You are a world-class Conversion Rate Optimization (CRO) expert and Web Design Consultant.
Analyze the following website text content and provide a professional, qualitative review.

Website URL: {url}

Website Content (Text Extract):
{text_content}

Please analyze the following 4 areas and provide a score (0-10) and a brief, actionable observation for each:

1. **Value Proposition**: Is it clear what they do and why it matters?
2. **Copywriting**: Is the language persuasive, clear, and professional?
3. **Trust Factors**: Do they have testimonials, clear contact info, or social proof?
4. **Call to Action (CTA)**: Are next steps clear and compelling?

Format your response as a valid JSON object with this structure:
{{
  "value_proposition": {{ "score": 0, "observation": "..." }},
  "copywriting": {{ "score": 0, "observation": "..." }},
  "trust_factors": {{ "score": 0, "observation": "..." }},
  "cta": {{ "score": 0, "observation": "..." }},
  "summary": "A 2-sentence overall summary of the website's effectiveness."
}}
"""
