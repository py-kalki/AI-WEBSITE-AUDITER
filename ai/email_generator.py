import os
import requests
import json

class EmailGenerator:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={self.api_key}"

    def generate(self, business_info, audit_data, template):
        """
        Generate a personalized email based on the template and audit data.
        
        Args:
            business_info (dict): Info about the business (name, website, etc.)
            audit_data (dict): Audit scores and details.
            template (str): The user-provided email template.
            
        Returns:
            str: The generated email body.
        """
        if not self.api_key:
            return "Error: GEMINI_API_KEY not found."

        prompt = self.create_prompt(business_info, audit_data, template)
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 800
            }
        }
        
        try:
            response = requests.post(self.api_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    return result['candidates'][0]['content']['parts'][0]['text'].strip()
                else:
                    return "Error: No email generated."
            else:
                return f"Error generating email: {response.status_code} - {response.text}"
        except Exception as e:
            return f"Error generating email: {str(e)}"

    def create_prompt(self, business_info, audit_data, template):
        """Create a prompt for the AI to fill the template."""
        business_name = business_info.get('business_name', 'the business')
        website = business_info.get('website', 'their website')
        
        # Extract scores
        perf = audit_data.get('performance_score', 0)
        seo = audit_data.get('seo_score', 0)
        ux = audit_data.get('ux_score', 0)
        mobile = audit_data.get('mobile_score', 0)
        overall = audit_data.get('overall_score', 0)
        
        # Extract key issues if available
        issues = []
        if 'performance' in audit_data and 'issues' in audit_data['performance']:
            issues.extend(audit_data['performance']['issues'][:2])
        if 'seo' in audit_data and 'issues' in audit_data['seo']:
            issues.extend(audit_data['seo']['issues'][:2])
            
        issues_str = "\n- ".join(issues) if issues else "General optimization opportunities"

        prompt = f"""
You are an expert sales copywriter. Your goal is to write a personalized cold email using the provided template.
You must strictly follow the template structure but fill in the placeholders with specific details from the audit data to make it personal.

**Business Details:**
- Name: {business_name}
- Website: {website}

**Audit Results:**
- Overall Score: {overall}/100
- Performance: {perf}/100
- SEO: {seo}/100
- UX: {ux}/100
- Mobile: {mobile}/100

**Key Issues Found:**
- {issues_str}

**User Template:**
{template}

**Instructions:**
1. Replace any placeholders in the template (like {{Name}}, {{Score}}, etc.) with actual data.
2. If the template asks for "specific issues" or "observations", use the Audit Results and Key Issues to write a sentence or two about what is wrong with their site.
3. Keep the tone professional but persuasive.
4. Output ONLY the email body. Do not include subject line unless the template has a specific place for it.
"""
        return prompt
