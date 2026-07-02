from sentence_transformers import SentenceTransformer

from app.config import MODEL_PATH

_model: SentenceTransformer | None = None


def load_model() -> SentenceTransformer:
    global _model

    if _model is None:
        _model = SentenceTransformer(
            MODEL_PATH,
            local_files_only=True,
        )

    return _model


def build_embedding(text: str) -> list[float]:
    model = load_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()
