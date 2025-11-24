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
page = st.sidebar.radio("Go to", ["Scrape", "Leads", "Audit", "Reports", "Mass Outreach"])

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
            
            # Display AI Qualitative Review if available
            if 'ai_review' in audit_data_dict and 'error' not in audit_data_dict['ai_review']:
                review = audit_data_dict['ai_review']
                st.markdown("### 🤖 AI Professional Review")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Value Proposition**: {review.get('value_proposition', {}).get('score', 0)}/10")
                    st.info(review.get('value_proposition', {}).get('observation', 'N/A'))
                    
                    st.markdown(f"**Copywriting**: {review.get('copywriting', {}).get('score', 0)}/10")
                    st.info(review.get('copywriting', {}).get('observation', 'N/A'))
                    
                with col2:
                    st.markdown(f"**Trust Factors**: {review.get('trust_factors', {}).get('score', 0)}/10")
                    st.info(review.get('trust_factors', {}).get('observation', 'N/A'))
                    
                    st.markdown(f"**Call to Action**: {review.get('cta', {}).get('score', 0)}/10")
                    st.info(review.get('cta', {}).get('observation', 'N/A'))
                    
                st.success(f"**Summary**: {review.get('summary', 'N/A')}")
                st.divider()

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

elif page == "Mass Outreach":
    st.header("Mass Cold Email Outreach")
    
    # Configuration
    with st.expander("Configuration", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            source = st.selectbox("Source", ["Google Maps", "JustDial"], key="mass_source")
            keyword = st.text_input("Keyword", key="mass_keyword")
        with col2:
            location = st.text_input("Location", key="mass_location")
            # Fixed at 15 leads as per requirement, but editable if needed
            total = st.number_input("Leads to Generate", value=15, min_value=1, max_value=50, key="mass_total")
            
        st.subheader("Email Template")
        default_template = """Subject: Quick question about {Business}

Hi,

I came across your website {Website} and noticed a few things that could be improved.
We ran a quick audit and your site scored {Overall}/100.

Key issues we found:
{Issues}

We can help you fix these and get more customers. Are you available for a quick chat?

Best,
[Your Name]"""
        template = st.text_area("Email Template", value=default_template, height=300, help="Use placeholders like {Business}, {Website}, {Overall}, {Issues}")
        
        st.subheader("SMTP Settings (Optional - for sending)")
        with st.expander("SMTP Credentials"):
            smtp_server = st.text_input("SMTP Server", value="smtp.gmail.com")
            smtp_port = st.text_input("SMTP Port", value="587")
            smtp_user = st.text_input("SMTP Email")
            smtp_pass = st.text_input("SMTP Password", type="password")

    if st.button("🚀 Start Mass Outreach Campaign", type="primary"):
        if not keyword or not location:
            st.error("Please enter Keyword and Location.")
        else:
            status_container = st.container()
            log_container = st.empty()
            progress_bar = st.progress(0)
            
            logs = []
            def log(message):
                logs.append(message)
                log_container.code("\n".join(logs))
            
            # 1. Scrape
            log(f"Step 1: Scraping {total} leads from {source}...")
            results = asyncio.run(run_scraper_async(source, keyword, location, total))
            
            if not results:
                log("No leads found. Stopping.")
                st.error("No leads found.")
            else:
                log(f"Found {len(results)} raw leads.")
                
                # 2. Filter
                valid_leads = [l for l in results if l.get('email') and l.get('email') != 'N/A' and l.get('website') and l.get('website') != 'N/A']
                log(f"Filtered to {len(valid_leads)} leads with Email & Website.")
                
                if not valid_leads:
                    st.warning("No valid leads found (with both email and website).")
                else:
                    # Save leads first
                    saved_leads = []
                    for l in valid_leads:
                        lid = insert_lead(l)
                        if lid:
                            l['id'] = lid
                            saved_leads.append(l)
                    
                    log(f"Saved {len(saved_leads)} leads to database.")
                    
                    # Initialize tools
                    from ai.email_generator import EmailGenerator
                    from utils.email_sender import EmailSender
                    
                    email_gen = EmailGenerator()
                    email_sender = EmailSender(smtp_server, smtp_port, smtp_user, smtp_pass)
                    
                    # 3. Process Loop
                    success_count = 0
                    for i, lead in enumerate(saved_leads):
                        progress = (i + 1) / len(saved_leads)
                        progress_bar.progress(progress)
                        
                        log(f"Processing {lead['business_name']} ({i+1}/{len(saved_leads)})...")
                        
                        # A. Audit
                        log(f"  - Running Audit for {lead['website']}...")
                        # Run audit logic (reusing main.py logic or calling direct if possible, but main.py is script)
                        # We will use subprocess to ensure clean state like in Audit page
                        try:
                            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                            process = subprocess.Popen(
                                [sys.executable, "main.py", "analyze", "--lead_id", str(lead['id'])],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True,
                                cwd=project_root
                            )
                            stdout, stderr = process.communicate(timeout=120)
                            
                            if process.returncode != 0:
                                log(f"  - Audit failed: {stderr}")
                                continue
                                
                            # Fetch audit result
                            audit = get_audit(lead['id'])
                            if not audit:
                                log("  - Audit data not found after run.")
                                continue
                                
                            audit_data = json.loads(audit['audit_data'])
                            # Merge scores
                            audit_data['performance_score'] = audit['performance_score']
                            audit_data['seo_score'] = audit['seo_score']
                            audit_data['ux_score'] = audit['ux_score']
                            audit_data['mobile_score'] = audit['mobile_score']
                            audit_data['overall_score'] = audit['overall_score']
                            
                            # B. Generate Email
                            log("  - Generating personalized email...")
                            email_body = email_gen.generate(lead, audit_data, template)
                            
                            # C. Send Email
                            if smtp_user and smtp_pass:
                                log(f"  - Sending email to {lead['email']}...")
                                sent, msg = email_sender.send_email(lead['email'], f"Question about {lead['business_name']}", email_body)
                                if sent:
                                    log("  - Email SENT successfully.")
                                    # Update DB status
                                    conn = get_connection()
                                    conn.execute("UPDATE leads SET outreach_status = ?, outreach_time = CURRENT_TIMESTAMP WHERE id = ?", ("Sent", lead['id']))
                                    conn.commit()
                                    conn.close()
                                    success_count += 1
                                else:
                                    log(f"  - Email Sending FAILED: {msg}")
                            else:
                                log("  - Email generated (Draft Mode - SMTP not set).")
                                log(f"  - Preview: {email_body[:50]}...")
                                # Save as draft status
                                conn = get_connection()
                                conn.execute("UPDATE leads SET outreach_status = ?, outreach_time = CURRENT_TIMESTAMP WHERE id = ?", ("Draft", lead['id']))
                                conn.commit()
                                conn.close()
                                success_count += 1
                                
                        except Exception as e:
                            log(f"  - Error processing lead: {e}")
                            
                    st.success(f"Campaign Completed! Successfully processed {success_count} leads.")
