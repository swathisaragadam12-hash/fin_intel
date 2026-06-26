# config.py
import os
from dotenv import load_dotenv

# Load workspace environment variables from a local .env file
load_dotenv()

# Extract and validate credentials securely
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError(
        "CRITICAL ERROR: GOOGLE_API_KEY is missing from the environment variables. "
        "Please check your local .env file configurations."
    )

# Unified Global Parameters
MODEL_NAME = "gemini-2.5-flash"
OUTPUT_REPORT_PATH = "financial_report.pdf"