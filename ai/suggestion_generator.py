import requests
import os
import json

class SuggestionGenerator:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={self.api_key}"

    def generate(self, business_info, audit_summary):
        """Generate AI-powered suggestions based on audit data."""
        if not self.api_key:
            return "Error: GEMINI_API_KEY not found in environment variables. Please add it to your .env file.\n\nGet a free API key at: https://makersuite.google.com/app/apikey"
        
        # Create a detailed prompt
        prompt = self.create_prompt(business_info, audit_summary)
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 500
            }
        }
        
        try:
            response = requests.post(self.api_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    return result['candidates'][0]['content']['parts'][0]['text'].strip()
                else:
                    return "No suggestion generated."
            else:
                return f"Error generating suggestion: {response.status_code} - {response.text}"
        except Exception as e:
            return f"Error generating suggestion: {str(e)}"

    def create_prompt(self, business_info, audit_summary):
        """Create a structured prompt for the AI."""
        business_name = business_info.get('business_name', 'Unknown Business')
        website = business_info.get('website', 'N/A')
        
        perf_score = audit_summary.get('performance_score', 0)
        seo_score = audit_summary.get('seo_score', 0)
        ux_score = audit_summary.get('ux_score', 0)
        mobile_score = audit_summary.get('mobile_score', 0)
        overall_score = audit_summary.get('overall_score', 0)
        
        prompt = f"""You are a professional web development consultant. Analyze this website audit and provide 3 specific, actionable recommendations.

Business: {business_name}
Website: {website}

Audit Scores:
- Performance: {perf_score}/100
- SEO: {seo_score}/100
- UX: {ux_score}/100
- Mobile: {mobile_score}/100
- Overall: {overall_score}/100

Provide exactly 3 specific, actionable recommendations to improve this website. Focus on the lowest-scoring areas. Format your response as:

1. [Area]: [Specific recommendation]
2. [Area]: [Specific recommendation]
3. [Area]: [Specific recommendation]

Keep each recommendation concise and actionable."""
        
        return prompt

if __name__ == "__main__":
    # Test with a dummy key or env var
    gen = SuggestionGenerator()
    # print(gen.generate({"business_name": "Test Biz", "category": "Test"}, {"overall_score": 50}))

