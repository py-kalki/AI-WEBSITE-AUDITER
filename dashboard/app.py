import streamlit as st
import pandas as pd
import os
import sys
import asyncio
import json
import subprocess
import sqlite3

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from storage.database import get_connection, insert_lead, delete_lead
from reporting.pdf_generator import PDFReportGenerator
from scraper.maps_scraper import MapsScraper
from scraper.justdial_scraper import JustDialScraper
from ai.suggestion_generator import SuggestionGenerator

# Fix for Windows asyncio loop with Playwright
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

st.set_page_config(page_title="AI Website Auditor", layout="wide")

st.title("AI Website Auditor Dashboard")

# Sidebar
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["Scrape", "Leads", "Audit", "Reports"])

def get_leads():
    """Fetch leads from database - always fresh data."""
    conn = get_connection()
    conn.row_factory = None  # Reset row factory
    conn.row_factory = sqlite3.Row  # Set it again
    df = pd.read_sql_query("SELECT * FROM leads ORDER BY created_at DESC", conn)
    conn.close()
    return df

def get_audit(lead_id):
    """Fetch audit from database - always fresh data."""
    conn = get_connection()
    conn.row_factory = None  # Reset row factory
    conn.row_factory = sqlite3.Row  # Set it again
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audits WHERE lead_id = ? ORDER BY created_at DESC LIMIT 1", (lead_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        # Convert to dict for easier access
        return dict(result)
    return None

async def run_scraper_async(source, keyword, location, total):
    results = []
    if source == "Google Maps":
        scraper = MapsScraper()
        results = await scraper.scrape(keyword, location, total)
    elif source == "JustDial":
        scraper = JustDialScraper()
        results = scraper.scrape(keyword, location, total)
    return results

if page == "Scrape":
    st.header("Lead Scraper")
    
    col1, col2 = st.columns(2)
    with col1:
        source = st.selectbox("Source", ["Google Maps", "JustDial"])
        keyword = st.text_input("Keyword (e.g., Dentist, Gym)")
    with col2:
        location = st.text_input("Location (e.g., New York, Mumbai)")
        total = st.number_input("Number of Leads", min_value=1, max_value=50, value=5)
        
    if st.button("Start Scraping"):
        if keyword and location:
            with st.spinner(f"Scraping {source} for {keyword} in {location}..."):
                # Run async scraper
                results = asyncio.run(run_scraper_async(source, keyword, location, total))
                
                if results:
                    st.success(f"Found {len(results)} potential leads!")
                    
                    # Filter to only keep leads with both email and website
                    filtered_results = [
                        lead for lead in results 
                        if lead.get('email') and lead.get('email') != 'N/A' 
                        and lead.get('website') and lead.get('website') != 'N/A'
                    ]
                    
                    if filtered_results:
                        count = 0
                        for lead in filtered_results:
                            if insert_lead(lead):
                                count += 1
                        st.info(f"Saved {count} leads with both email and website to database.")
                        st.warning(f"Filtered out {len(results) - len(filtered_results)} leads without email or website.")
                    else:
                        st.warning("No leads found with both email and website. Try a different search.")
                else:
                    st.warning("No leads found.")
        else:
            st.error("Please enter Keyword and Location.")

elif page == "Leads":
    st.header("Leads Management")
    leads = get_leads()
    
    if not leads.empty:
        # Display leads with delete option
        for index, row in leads.iterrows():
            col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
            with col1:
                st.write(f"**{row['business_name']}**")
            with col2:
                st.write(row['category'])
            with col3:
                email = row['email'] if 'email' in leads.columns and pd.notna(row['email']) else "N/A"
                st.write(email)
            with col4:
                st.write(row['website'] if row['website'] else "N/A")
            with col5:
                if st.button("Delete", key=f"del_{row['id']}"):
                    if delete_lead(row['id']):
                        st.success("Deleted!")
                        st.rerun()
                    else:
                        st.error("Failed")
        
        st.divider()
        st.subheader("Export Leads")
        
        # Convert DataFrame to CSV for download
        csv = leads.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name='leads_export.csv',
            mime='text/csv',
        )
    else:
        st.info("No leads found. Go to 'Scrape' page to find some.")

elif page == "Audit":
    st.header("Run Audit")
    leads = get_leads()
    
    if not leads.empty:
        selected_lead_name = st.selectbox("Select Business", leads['business_name'])
        selected_lead = leads[leads['business_name'] == selected_lead_name].iloc[0]
        
        # Ensure lead_id is an integer
        lead_id = int(selected_lead['id'])
        
        st.write(f"**Selected:** {selected_lead['business_name']}")
        st.write(f"**Website:** {selected_lead['website']}")
        st.write(f"**Email:** {selected_lead.get('email', 'N/A')}")
        
        # Auto-Audit Button
        if st.button("Start Full Audit"):
            with st.spinner(f"Auditing {selected_lead['website']}... This may take a minute."):
                try:
                    # Get the project root directory (parent of dashboard folder)
                    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    
                    # Run the main.py analyze command as a subprocess
                    process = subprocess.Popen(
                        [sys.executable, "main.py", "analyze", "--lead_id", str(lead_id)],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        cwd=project_root  # Use project root as working directory
                    )
                    
                    # Wait for the process to complete (this blocks until done)
                    stdout, stderr = process.communicate(timeout=120)  # 2 minute timeout
                    
                    if process.returncode == 0:
                        st.success("✅ Audit completed successfully!")
                        st.text(stdout)  # Show the output
                        st.info("💡 Click the '🔄 Refresh Data' button in the Reports section to generate the PDF report.")
                    else:
                        st.error(f"❌ Audit failed!")
                        st.text(f"Error: {stderr}")
                        st.text(f"Output: {stdout}")
                except subprocess.TimeoutExpired:
                    st.error("⏱️ Audit timed out (took longer than 2 minutes)")
                    process.kill()
                except Exception as e:
                    st.error(f"❌ Error running audit: {e}")

        # Show existing audit if available
        audit = get_audit(lead_id)
        if audit is not None:
            st.success("Audit Results Available")
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Performance", audit['performance_score'])
            col2.metric("SEO", audit['seo_score'])
            col3.metric("UX", audit['ux_score'])
            col4.metric("Overall", audit['overall_score'])
            
            # AI Summary
            st.subheader("AI Analysis & Suggestions")
            
            try:
                audit_data_dict = json.loads(audit['audit_data'])
            except:
                audit_data_dict = {}
                
            if st.button("Generate AI Summary"):
                with st.spinner("Generating AI suggestions..."):
                    # Prepare data
                    audit_data_dict['performance_score'] = audit['performance_score']
                    audit_data_dict['seo_score'] = audit['seo_score']
                    audit_data_dict['ux_score'] = audit['ux_score']
                    audit_data_dict['mobile_score'] = audit['mobile_score']
                    audit_data_dict['overall_score'] = audit['overall_score']
                    
                    gen = SuggestionGenerator()
                    suggestion = gen.generate(dict(selected_lead), audit_data_dict)
                    
                    st.markdown(f"### AI Insights\n{suggestion}")
            
            with st.expander("View Raw Audit Data"):
                st.json(audit['audit_data'])
        else:
            st.info("No audit data yet. Click 'Start Full Audit' to begin.")
            
    else:
        st.info("No leads available.")

elif page == "Reports":
    st.header("Generate Reports")
    
    # Add refresh button
    if st.button("🔄 Refresh Data"):
        st.rerun()
    
    leads = get_leads()
    
    if not leads.empty:
        selected_lead_name = st.selectbox("Select Business for Report", leads['business_name'], key="report_selectbox")
        selected_lead = leads[leads['business_name'] == selected_lead_name].iloc[0]
        
        # Ensure lead_id is an integer
        lead_id = int(selected_lead['id'])
        
        st.write(f"**Business:** {selected_lead['business_name']}")
        st.write(f"**Website:** {selected_lead['website']}")
        
        audit = get_audit(lead_id)
        
        if audit is not None:
            st.success(f"✅ Audit Available - Overall Score: {audit['overall_score']}/100")
            
            # Show score breakdown
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Performance", f"{audit['performance_score']}/100")
            col2.metric("SEO", f"{audit['seo_score']}/100")
            col3.metric("UX", f"{audit['ux_score']}/100")
            col4.metric("Mobile", f"{audit['mobile_score']}/100")
            
            st.divider()
            
            if st.button("📄 Generate PDF Report"):
                filename = f"report_{lead_id}.pdf"
                filepath = os.path.join("reports", filename)
                
                try:
                    audit_data_dict = json.loads(audit['audit_data'])
                    audit_data_dict['performance_score'] = audit['performance_score']
                    audit_data_dict['seo_score'] = audit['seo_score']
                    audit_data_dict['ux_score'] = audit['ux_score']
                    audit_data_dict['mobile_score'] = audit['mobile_score']
                    audit_data_dict['overall_score'] = audit['overall_score']
                except Exception as e:
                    st.error(f"Error parsing audit data: {e}")
                    audit_data_dict = {}
                
                # Generate AI suggestion for the report
                with st.spinner("Generating AI suggestions..."):
                    gen_ai = SuggestionGenerator()
                    suggestions = gen_ai.generate(dict(selected_lead), audit_data_dict)
                
                with st.spinner("Creating PDF..."):
                    gen = PDFReportGenerator()
                    if gen.generate(dict(selected_lead), audit_data_dict, suggestions, filepath):
                        st.success(f"✅ Report generated successfully!")
                        with open(filepath, "rb") as f:
                            st.download_button("⬇️ Download PDF Report", f, file_name=filename, mime="application/pdf")
                    else:
                        st.error("Failed to generate report.")
        else:
            st.warning("⚠️ No audit data found.")
            st.info(f"Please run an audit for '{selected_lead['business_name']}' in the Audit section first.")
    else:
        st.info("No leads available. Go to the Scrape section to find leads.")
