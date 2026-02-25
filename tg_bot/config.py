from pathlib import Path
import os
from dotenv import load_dotenv


load_dotenv()

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB
USER_ERROR_REPORT_LEVEL = 25

API_URL = os.getenv("API_URL", "http://localhost:8000/predict")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN not set")

BASE_DIR = Path(__file__).resolve().parent.parent
TMP_DIR= BASE_DIR / "tmp"
LOG_DIR = BASE_DIR / "logs"