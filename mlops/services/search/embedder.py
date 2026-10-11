from __future__ import annotations

_model = None


def get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
    return _model


def embed(text: str) -> list[float]:
    vector = get_model().encode(text, normalize_embeddings=True)
    return [float(x) for x in vector.tolist()]
