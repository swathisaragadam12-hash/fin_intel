import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError(
        "GOOGLE_API_KEY not found.\n"
        "Create a .env file and add:\n\n"
        "GOOGLE_API_KEY=your_api_key"
    )

MODEL_NAME = "gemini-2.5-flash"

REPORTS_DIR = "reports"

os.makedirs(REPORTS_DIR, exist_ok=True)