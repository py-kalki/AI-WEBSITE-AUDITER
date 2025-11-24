import sys
import os

# Add parent directory to path
sys.path.append(os.getcwd())

from ai.email_generator import EmailGenerator
from utils.email_sender import EmailSender

def test_email_gen():
    print("Testing EmailGenerator...")
    gen = EmailGenerator(api_key="test_key") # Dummy key, just checking class structure
    
    # Mock data
    biz = {"business_name": "Test Biz", "website": "example.com"}
    audit = {"overall_score": 50, "performance_score": 40, "seo_score": 60, "ux_score": 50, "mobile_score": 50, "performance": {"issues": ["Slow load"]}}
    template = "Hi {Business}, score {Overall}. {Issues}"
    
    prompt = gen.create_prompt(biz, audit, template)
    print("Prompt created successfully.")
    # We won't call generate() as it hits API, but we verified imports and prompt creation.

def test_email_sender():
    print("Testing EmailSender...")
    sender = EmailSender("smtp.test.com", 587, "user", "pass")
    # Just checking init
    print("EmailSender initialized.")

if __name__ == "__main__":
    try:
        test_email_gen()
        test_email_sender()
        print("All tests passed!")
    except Exception as e:
        print(f"Test failed: {e}")
