from pathlib import Path
import os

from dotenv import load_dotenv
from huggingface_hub import snapshot_download

# Загружаем переменные окружения из файла .env
load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

if HF_TOKEN is None:
    raise RuntimeError("Переменная окружения HF_TOKEN не найдена. Добавьте ее в файл .env")

MODEL_NAME = "BAAI/bge-m3"

LOCAL_DIR = Path("models/bge-m3")
LOCAL_DIR.mkdir(parents=True, exist_ok=True)

snapshot_download(repo_id=MODEL_NAME, local_dir=str(LOCAL_DIR), token=HF_TOKEN)
