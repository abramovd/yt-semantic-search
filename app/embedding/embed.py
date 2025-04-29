import numpy as np

from sentence_transformers import SentenceTransformer

model_name = "all-MiniLM-L6-v2"
model = SentenceTransformer(model_name)

def embed_text(text: str) -> np.ndarray:
    """
    Embed a single string into a 1D numpy array of floats.
    """
    # convert_to_numpy=True returns a numpy array; otherwise you get a torch.Tensor
    vec = model.encode(text, convert_to_numpy=True, show_progress_bar=False)
    return vec

def embed_texts(texts: list[str], batch_size: int = 32) -> np.ndarray:
    """
    Embed a list of strings into a 2D numpy array (shape: [len(texts), dim]).
    Processes in batches for speed/memory control.
    """
    vecs = model.encode(
        texts,
        batch_size=batch_size,
        convert_to_numpy=True,
        show_progress_bar=True
    )
    return vecs
