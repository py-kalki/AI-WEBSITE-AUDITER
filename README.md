# 🚀 AI Website Auditor

An intelligent, automated lead generation and website auditing tool that helps you find potential clients, analyze their websites, and generate professional audit reports with AI-powered recommendations.

## ✨ Features

### 🔍 **Lead Scraping**
- Scrape business leads from Google Maps
- Extract contact information (email, phone, website)
- Filter leads with both email and website
- Export leads to CSV

### 📊 **Website Auditing**
- **Performance Analysis**: Page load speed, optimization metrics
- **SEO Analysis**: Meta tags, headings, keyword optimization
- **UX Analysis**: User experience and accessibility
- **Mobile Responsiveness**: Mobile-friendly testing
- **Broken Links Detection**: Find and report broken links

### 🤖 **AI-Powered Insights**
- Generate actionable recommendations using Google Gemini AI
- Tailored suggestions based on audit scores
- Professional business advice

### 📄 **PDF Report Generation**
- Beautiful, professional PDF reports
- Complete audit breakdown with scores
- AI-generated improvement suggestions
- Ready to send to clients

### 💻 **Interactive Dashboard**
- Modern Streamlit-based UI
- Real-time audit execution
- Lead management (view, delete, export)
- One-click report generation

## 🛠️ Tech Stack

- **Python 3.8+**
- **Streamlit** - Dashboard UI
- **Playwright** - Web scraping & browser automation
- **BeautifulSoup4** - HTML parsing & email extraction
- **ReportLab** - PDF generation
- **SQLite** - Database storage
- **Google Gemini API** - AI suggestions

## 📦 Installation

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd "AI Automation"
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install Playwright Browsers
```bash
playwright install
```

### 4. Set Up Environment Variables
Create a `.env` file in the project root:
```env
# Get a free API key at: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here
```

### 5. Initialize Database
```bash
python main.py init
```

## 🚀 Usage

### Start the Dashboard
```bash
python main.py dashboard
```

Then open your browser to `http://localhost:8501`

### Dashboard Sections

#### 1️⃣ **Scrape**
- Select source (Google Maps)
- Enter keyword (e.g., "Architects", "Dentists")
- Enter location (e.g., "Bangalore", "New York")
- Set number of leads to scrape
- Click "Start Scraping"

#### 2️⃣ **Leads**
- View all scraped leads
- See business name, category, email, website
- Delete unwanted leads
- Export leads to CSV

#### 3️⃣ **Audit**
- Select a business to audit
- Click "Start Full Audit" (takes 1-2 minutes)
- View audit scores and metrics
- Generate AI summary with recommendations

#### 4️⃣ **Reports**
- Select an audited business
- View score breakdown
- Click "Generate PDF Report"
- Download professional PDF report

### CLI Commands

```bash
# Initialize database
python main.py init

# Scrape leads
python main.py scrape --source maps --keyword "Architects" --location "Bangalore" --total 10

# Run audit for a specific lead
python main.py analyze --lead_id 1

# Generate PDF report
python main.py report --lead_id 1

# Launch dashboard
python main.py dashboard
```

## 📁 Project Structure

```
AI Automation/
├── ai/
│   └── suggestion_generator.py    # AI-powered recommendations
├── analysis/
│   ├── performance_analyzer.py    # Performance metrics
│   ├── seo_analyzer.py            # SEO analysis
│   ├── ux_analyzer.py             # UX analysis
│   ├── mobile_test.py             # Mobile testing
│   └── broken_links_checker.py    # Link validation
├── dashboard/
│   └── app.py                     # Streamlit dashboard
├── reporting/
│   └── pdf_generator.py           # PDF report creation
├── scraper/
│   ├── maps_scraper.py            # Google Maps scraper
│   ├── email_extractor.py         # Email extraction
│   └── justdial_scraper.py        # JustDial scraper
├── storage/
│   ├── database.py                # SQLite database
│   └── leads.db                   # Database file
├── reports/                       # Generated PDF reports
├── .env                           # Environment variables
├── .gitignore                     # Git ignore rules
├── config.py                      # Configuration
├── main.py                        # CLI entry point
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## 🔑 Getting a Free Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and paste it in your `.env` file

**Free Tier Limits:**
- 15 requests per minute
- 1 million tokens per day
- 1500 requests per day

## 🎯 Use Cases

- **Web Design Agencies**: Find and audit potential clients
- **SEO Consultants**: Generate leads and audit reports
- **Digital Marketing**: Identify businesses needing website improvements
- **Freelancers**: Automated prospecting and professional reports

## 🐛 Troubleshooting

### "No leads found"
- Try different keywords or locations
- Ensure Playwright browsers are installed
- Check your internet connection

### "Audit failed"
- Verify the website URL is accessible
- Some websites block automated access
- Try a different lead

### "AI suggestions not working"
- Check your `GEMINI_API_KEY` in `.env`
- Verify you haven't exceeded rate limits
- Wait 1 minute and try again

### "Database errors"
- Run `python main.py init` to reinitialize
- Delete `storage/leads.db` and reinitialize

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## 📧 Support

For issues or questions, please open an issue on GitHub.

---

**Built with ❤️ using Python, Streamlit, and Google Gemini AI**
