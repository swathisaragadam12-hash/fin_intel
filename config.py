import os
from pathlib import Path
from dotenv import load_dotenv

# ==========================================================
# Load Environment Variables
# ==========================================================

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError(
        "GOOGLE_API_KEY not found.\n"
        "Create a .env file containing:\n\n"
        "GOOGLE_API_KEY=your_api_key"
    )

# ==========================================================
# Gemini Configuration
# ==========================================================

MODEL_NAME = "gemini-2.5-flash"

TEMPERATURE = 0.2

# ==========================================================
# Project Directories
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent

REPORTS_DIR = BASE_DIR / "reports"
CHARTS_DIR = BASE_DIR / "charts"

REPORTS_DIR.mkdir(exist_ok=True)
CHARTS_DIR.mkdir(exist_ok=True)

# ==========================================================
# Dashboard Settings
# ==========================================================

HISTORY_PERIOD = "1y"

FIGURE_SIZE = (10, 5)
SHORT_MA = 50
LONG_MA = 200

# ==========================================================
# Chart Output Files
# ==========================================================

PRICE_CHART = CHARTS_DIR / "price_chart.png"
VOLUME_CHART = CHARTS_DIR / "volume_chart.png"
MOVING_AVERAGE_CHART = CHARTS_DIR / "moving_average_chart.png"
REVENUE_CHART = CHARTS_DIR / "revenue_chart.png"
MARKETCAP_CHART = CHARTS_DIR / "market_cap_comparison.png"

# ==========================================================
# Report Output
# ==========================================================

REPORT_FILE = REPORTS_DIR / "financial_report.pdf"