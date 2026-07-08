import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_URL = os.getenv("DATABASE_URL")

MODEL_PATH = os.getenv("MODEL_PATH", str(BASE_DIR / "models" / "bge-m3"))
