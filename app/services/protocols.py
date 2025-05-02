import numpy as np

from typing import Protocol
from youtube_transcript_api import FetchedTranscript
from sentence_transformers import SentenceTransformer

from app.chunking.chunk import Chunk
from app.storage.models import Document, SearchResultChunk


class TranscriptChunker(Protocol):
    def split_into_chunks(self, transcript: FetchedTranscript) -> list[Chunk]:
        ...


class Embedder(Protocol):
    def embed_text(self, text: str) -> np.ndarray:
        ...

    def embed_texts(self, texts: list[str], batch_size: int = 32) -> np.ndarray:
        ...

    def get_model(self) -> SentenceTransformer:
        ...


class TranscriptFetcher(Protocol):
    def fetch(self, video_id: str) -> FetchedTranscript:
        ...


class ReadOnlyRepository(Protocol):
    def list_documents(self) -> list[Document]:
        ...

    def get_document(self, document_id: int) -> Document:
        ...

    def is_document_exists(self, url: str) -> bool:
        ...


class Repository(ReadOnlyRepository):
    def insert_document(self, document: Document) -> int:
        ...

    def insert_chunk(self, chunk: Chunk):
        ...

    def insert_chunks(self, chunks: list[Chunk]):
        ...

    def search(self, query_vector: np.ndarray, num_neighbors: int) -> list[SearchResultChunk]:
        ...

