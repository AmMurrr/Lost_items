from sentence_transformers import SentenceTransformer

from app.config import MODEL_PATH
from logs.logs import logger

_model: SentenceTransformer | None = None


def load_model() -> SentenceTransformer:
    global _model

    if _model is None:
        logger.info("Загружаю модель эмбеддингов из %s", MODEL_PATH)
        _model = SentenceTransformer(
            MODEL_PATH,
            local_files_only=True,
        )
        logger.info("Модель эмбеддингов загружена")

    return _model


def build_embedding(text: str) -> list[float]:
    model = load_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()
