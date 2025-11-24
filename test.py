import asyncio
import os
import sys
import traceback
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from storage.database import init_db, insert_lead, get_connection
from ai.score_calculator import ScoreCalculator
from ai.suggestion_generator import SuggestionGenerator
from reporting.pdf_generator import PDFReportGenerator
# Import analysis modules
from analysis.performance_analyzer import PerformanceAnalyzer
from analysis.seo_analyzer import SEOAnalyzer
from analysis.ux_analyzer import UXAnalyzer
from analysis.mobile_test import MobileTest
from analysis.broken_links_checker import BrokenLinksChecker

# Import scrapers (Mocking might be needed for full automation without network, but we'll try to instantiate)
from scraper.maps_scraper import MapsScraper
from scraper.justdial_scraper import JustDialScraper

def print_result(module, status, message=""):
    color = "\033[92m" if status else "\033[91m" # Green for True, Red for False
    reset = "\033[0m"
    status_text = "TRUE" if status else "FALSE"
    print(f"[{module}] {color}{status_text}{reset} {message}")

async def test_storage():
    try:
        init_db()
        lead = {
            "business_name": "Test Storage",
            "category": "Test",
            "address": "123 Test",
            "phone": "000",
            "website": "example.com",
            "source": "Test"
        }
        lead_id = insert_lead(lead)
        if not lead_id:
            return False, "Failed to insert lead"
        
        conn = get_connection()
        row = conn.execute("SELECT * FROM leads WHERE id = ?", (lead_id,)).fetchone()
        conn.close()
        
        if row and row['business_name'] == "Test Storage":
            return True, ""
        else:
            return False, "Retrieved data does not match"
    except Exception as e:
        return False, f"Exception: {str(e)}"

def test_ai_score():
    try:
        calc = ScoreCalculator()
        p = {"score": 80}
        s = {"score": 80}
        u = {"score": 80}
        m = {"score": 80}
        l = {"score": 100} # 100 means no broken links penalty usually, or 0 broken links
        # Logic: 80*0.25 + 80*0.25 + 80*0.20 + 80*0.20 + 100*0.10 = 20+20+16+16+10 = 82
        score = calc.calculate(p, s, u, m, l)
        if score == 82:
            return True, ""
        else:
            return False, f"Calculation mismatch. Expected 82, got {score}"
    except Exception as e:
        return False, f"Exception: {str(e)}"

def test_ai_suggestions():
    try:
        # Check if API key is loaded from env
        api_key = os.getenv("HF_API_KEY")
        if not api_key:
            return False, "HF_API_KEY not found in environment"
            
        gen = SuggestionGenerator()
        if gen.api_key == api_key:
            return True, ""
        return False, "Generator did not load API key correctly"
    except Exception as e:
        return False, f"Exception: {str(e)}"

def test_reporting():
    try:
        gen = PDFReportGenerator()
        lead = {"business_name": "Test Report", "category": "Test", "website": "example.com"}
        audit = {
            "performance_score": 80, "seo_score": 80, "ux_score": 80, "mobile_score": 80, "overall_score": 80,
            "priorities": [{"priority": "High", "category": "Test", "issue": "Test Issue"}]
        }
        filename = "test_suite_report.pdf"
        if os.path.exists(filename):
            os.remove(filename)
            
        success = gen.generate(lead, audit, "Test Suggestion", filename)
        if success and os.path.exists(filename):
            os.remove(filename) # Cleanup
            return True, ""
        else:
            return False, "Report generation returned False or file not created"
    except Exception as e:
        return False, f"Exception: {str(e)}"

def test_analysis_modules():
    results = {}
    
    # Performance
    try:
        perf = PerformanceAnalyzer()
        # Mocking analyze to avoid network call or just checking instantiation
        if perf:
             results['PerformanceAnalyzer'] = (True, "")
        else:
             results['PerformanceAnalyzer'] = (False, "Init failed")
    except Exception as e:
        results['PerformanceAnalyzer'] = (False, str(e))

    # SEO
    try:
        seo = SEOAnalyzer()
        if seo:
             results['SEOAnalyzer'] = (True, "")
    except Exception as e:
        results['SEOAnalyzer'] = (False, str(e))

    # UX
    try:
        ux = UXAnalyzer()
        if ux:
             results['UXAnalyzer'] = (True, "")
    except Exception as e:
        results['UXAnalyzer'] = (False, str(e))

    # Broken Links
    try:
        bl = BrokenLinksChecker()
        if bl:
             results['BrokenLinksChecker'] = (True, "")
    except Exception as e:
        results['BrokenLinksChecker'] = (False, str(e))

    return results

async def test_mobile_analysis():
    try:
        mobile = MobileTest()
        if mobile:
            return True, ""
        return False, "Init failed"
    except Exception as e:
        return False, str(e)

async def test_scrapers():
    results = {}
    try:
        maps = MapsScraper()
        if maps:
            results['MapsScraper'] = (True, "")
    except Exception as e:
        results['MapsScraper'] = (False, str(e))
        
    try:
        jd = JustDialScraper()
        if jd:
            results['JustDialScraper'] = (True, "")
    except Exception as e:
        results['JustDialScraper'] = (False, str(e))
        
    return results

async def main():
    print("Running System Tests...\n")
    
    # Storage
    s_status, s_msg = await test_storage()
    print_result("Storage", s_status, s_msg)
    
    # AI
    ai_status, ai_msg = test_ai_score()
    print_result("AI Score", ai_status, ai_msg)
    
    ai_sug_status, ai_sug_msg = test_ai_suggestions()
    print_result("AI Suggestions", ai_sug_status, ai_sug_msg)
    
    # Reporting
    rep_status, rep_msg = test_reporting()
    print_result("Reporting", rep_status, rep_msg)
    
    # Analysis
    an_results = test_analysis_modules()
    for mod, (status, msg) in an_results.items():
        print_result(mod, status, msg)
        
    mob_status, mob_msg = await test_mobile_analysis()
    print_result("MobileTest", mob_status, mob_msg)
    
    # Scrapers
    sc_results = await test_scrapers()
    for mod, (status, msg) in sc_results.items():
        print_result(mod, status, msg)

if __name__ == "__main__":
    asyncio.run(main())
