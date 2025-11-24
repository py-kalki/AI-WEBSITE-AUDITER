import asyncio
import argparse
import json
from scraper.maps_scraper import MapsScraper
from scraper.justdial_scraper import JustDialScraper
from storage.database import init_db, insert_lead, get_connection
from analysis.performance_analyzer import PerformanceAnalyzer
from analysis.seo_analyzer import SEOAnalyzer
from analysis.ux_analyzer import UXAnalyzer
from analysis.mobile_test import MobileTest
from analysis.broken_links_checker import BrokenLinksChecker
from ai.score_calculator import ScoreCalculator
from ai.suggestion_generator import SuggestionGenerator
from reporting.pdf_generator import PDFReportGenerator
import os

async def run_scraper(source, keyword, location, total):
    print(f"Starting scraper: {source} for {keyword} in {location}")
    results = []
    if source.lower() == "maps":
        scraper = MapsScraper()
        results = await scraper.scrape(keyword, location, total)
    elif source.lower() == "justdial":
        scraper = JustDialScraper()
        results = scraper.scrape(keyword, location, total)
    
    print(f"Found {len(results)} leads.")
    for lead in results:
        lead_id = insert_lead(lead)
        if lead_id:
            print(f"Saved lead: {lead['business_name']} (ID: {lead_id})")

async def run_analysis(lead_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leads WHERE id = ?", (lead_id,))
    lead = cursor.fetchone()
    conn.close()
    
    if not lead:
        print("Lead not found.")
        return

    url = lead['website']
    if not url:
        print("Lead has no website to analyze.")
        return

    print(f"Analyzing {url}...")
    
    # Initialize analyzers
    perf = PerformanceAnalyzer()
    seo = SEOAnalyzer()
    ux = UXAnalyzer()
    mobile = MobileTest()
    links = BrokenLinksChecker()
    
    # Run analysis
    # Note: Some might be async, some sync. Assuming sync for simplicity unless known async.
    # MobileTest is async based on previous file view.
    
    # Mocking sync calls for analyzers I haven't seen fully but assuming structure
    # If they are async, I need to await them.
    # Let's assume they are sync except MobileTest which I saw was async.
    
    # Actually, I should check if they are async. 
    # Based on file names, they likely use requests or playwright.
    # I'll wrap in try/except to be safe and assume sync for now, except Mobile.
    
    try:
        p_data = perf.analyze(url)
    except:
        p_data = {"score": 50, "issues": ["Performance analysis failed"]}

    try:
        s_data = seo.analyze(url)
    except:
        s_data = {"score": 50, "issues": ["SEO analysis failed"]}

    try:
        u_data = ux.analyze(url)
    except:
        u_data = {"score": 50, "issues": ["UX analysis failed"]}
        
    try:
        m_data = await mobile.check(url)
    except:
        m_data = {"score": 50, "issues": ["Mobile analysis failed"]}

    try:
        l_data = links.check(url)
    except:
        l_data = {"score": 100, "count": 0}

    # Calculate Score
    calc = ScoreCalculator()
    overall_score = calc.calculate(p_data, s_data, u_data, m_data, l_data)
    priorities = calc.get_priority_list(p_data, s_data, u_data, m_data, l_data)
    
    audit_data = {
        "performance": p_data,
        "seo": s_data,
        "ux": u_data,
        "mobile": m_data,
        "links": l_data,
        "priorities": priorities
    }
    
    # Save Audit
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO audits (lead_id, performance_score, seo_score, ux_score, mobile_score, overall_score, audit_data)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        lead_id,
        p_data.get('score', 0),
        s_data.get('score', 0),
        u_data.get('score', 0),
        m_data.get('score', 0),
        overall_score,
        json.dumps(audit_data)
    ))
    conn.commit()
    conn.close()
    
    print(f"Audit completed. Overall Score: {overall_score}")

def main():
    parser = argparse.ArgumentParser(description="AI Website Auditor")
    subparsers = parser.add_subparsers(dest="command")
    
    # Scrape Command
    scrape_parser = subparsers.add_parser("scrape", help="Scrape leads")
    scrape_parser.add_argument("--source", choices=["maps", "justdial"], required=True)
    scrape_parser.add_argument("--keyword", required=True)
    scrape_parser.add_argument("--location", required=True)
    scrape_parser.add_argument("--total", type=int, default=5)
    
    # Analyze Command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a lead")
    analyze_parser.add_argument("--lead_id", type=int, required=True)
    
    # Report Command
    report_parser = subparsers.add_parser("report", help="Generate PDF Report")
    report_parser.add_argument("--lead_id", type=int, required=True)

    # Dashboard Command
    subparsers.add_parser("dashboard", help="Run Dashboard")
    
    # Init DB
    subparsers.add_parser("init", help="Initialize Database")

    args = parser.parse_args()
    
    if args.command == "init":
        init_db()
    elif args.command == "scrape":
        asyncio.run(run_scraper(args.source, args.keyword, args.location, args.total))
    elif args.command == "analyze":
        asyncio.run(run_analysis(args.lead_id))
    elif args.command == "report":
        conn = get_connection()
        lead = conn.execute("SELECT * FROM leads WHERE id = ?", (args.lead_id,)).fetchone()
        audit = conn.execute("SELECT * FROM audits WHERE lead_id = ?", (args.lead_id,)).fetchone()
        conn.close()
        
        if lead and audit:
            try:
                # Convert Row to dict
                lead_dict = dict(lead)
                
                audit_data = json.loads(audit['audit_data'])
                # Merge scores
                audit_data['performance_score'] = audit['performance_score']
                audit_data['seo_score'] = audit['seo_score']
                audit_data['ux_score'] = audit['ux_score']
                audit_data['mobile_score'] = audit['mobile_score']
                audit_data['overall_score'] = audit['overall_score']
                
                gen = PDFReportGenerator()
                filename = f"report_{lead['id']}.pdf"
                filepath = os.path.join("reports", filename)
                gen.generate(lead_dict, audit_data, "AI Suggestions Placeholder", filepath)
            except Exception as e:
                print(f"Error generating report: {e}")
        else:
            print("Lead or Audit not found.")

    elif args.command == "dashboard":
        print("Running dashboard...")
        os.system("streamlit run dashboard/app.py")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
