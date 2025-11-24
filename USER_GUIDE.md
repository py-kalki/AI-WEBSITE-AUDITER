# AI Website Auditor - User Guide

Welcome to the AI Website Auditor! This tool helps you find business leads, audit their websites, and generate professional reports with AI-powered suggestions.

## Prerequisites
- Python 3.8+ installed.
- Google Chrome installed (for scraping).
- Hugging Face API Key (for AI features).

## Setup
1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    playwright install
    ```
2.  **Configure API Key**:
    - Open `.env` file.
    - Add your key: `HF_API_KEY=your_key_here`

## Running the App
The easiest way to use the tool is via the Dashboard.

### 1. Launch Dashboard
Run the following command in your terminal:
```bash
python main.py dashboard
```
This will open the app in your browser (usually at `http://localhost:8501`).

### 2. Scrape Leads
- Go to the **Scrape** page in the sidebar.
- Select Source (e.g., Google Maps).
- Enter Keyword (e.g., "Coffee Shop") and Location (e.g., "Seattle").
- Click **Start Scraping**.
- Leads will be saved to the database automatically.

### 3. Analyze & Audit
- Go to the **Audit** page.
- Select a business from the dropdown.
- View existing audit scores (Performance, SEO, UX, Mobile).
- Click **Generate AI Summary** to get actionable advice.

### 4. Generate Reports
- Go to the **Reports** page.
- Select a business.
- Click **Generate PDF Report**.
- Download the professional PDF report.

## Advanced Usage (CLI)
You can also use the command line for automation:

- **Scrape**:
  ```bash
  python main.py scrape --source maps --keyword "Gym" --location "London" --total 10
  ```
- **Analyze**:
  ```bash
  python main.py analyze --lead_id 1
  ```
- **Report**:
  ```bash
  python main.py report --lead_id 1
  ```

## Troubleshooting
- **Scraper Issues**: If scraping fails, ensure you have a stable internet connection and that Chrome is installed.
- **AI Errors**: If AI suggestions fail, check your `HF_API_KEY` in `.env`.
