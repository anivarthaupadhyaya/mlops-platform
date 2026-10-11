from __future__ import annotations

import threading

_model = None
_lock = threading.Lock()
_ready = False


def is_ready() -> bool:
    return _ready


def get_model():
    global _model, _ready
    with _lock:
        if _model is None:
            from sentence_transformers import SentenceTransformer

            _model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
            _ready = True
        return _model


def embed(text: str) -> list[float]:
    vector = get_model().encode(text, normalize_embeddings=True)
    return [float(x) for x in vector.tolist()]
