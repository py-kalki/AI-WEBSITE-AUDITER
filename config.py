import os
from dotenv import load_dotenv

load_dotenv()

# Base Directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database
DB_NAME = "leads.db"
DB_PATH = os.path.join(BASE_DIR, "storage", DB_NAME)

# Scraping
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
HEADLESS_MODE = True

# Reporting
REPORT_OUTPUT_DIR = os.path.join(BASE_DIR, "reports")
if not os.path.exists(REPORT_OUTPUT_DIR):
    os.makedirs(REPORT_OUTPUT_DIR)
