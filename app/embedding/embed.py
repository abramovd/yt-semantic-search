import numpy as np

from sentence_transformers import SentenceTransformer
from typing import Protocol
from functools import lru_cache


class SentenceTransformerEmbedder:
    def __init__(self, model_name: str):
        self.model_name = model_name

    @lru_cache
    def get_model(self) -> SentenceTransformer:
        return SentenceTransformer(self.model_name)

    def embed_text(self,text: str) -> np.ndarray:
        vec = self.get_model().encode(text, convert_to_numpy=True, show_progress_bar=False)
        return vec

    def embed_texts(self,texts: list[str], batch_size: int = 32) -> np.ndarray:
        vecs = self.get_model().encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            show_progress_bar=False
        )
        return vecs

def get_sentence_transformer_embedder(model_name: str) -> SentenceTransformerEmbedder:
    return SentenceTransformerEmbedder(model_name)
