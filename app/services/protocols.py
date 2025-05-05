import numpy as np

from typing import Protocol, Tuple
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
        """List all documents (legacy method)."""
        ...

    def list_documents_paginated(self, limit: int, offset: int) -> Tuple[list[Document], int]:
        """
        List documents with pagination.
        
        Args:
            limit: Maximum number of documents to return
            offset: Number of documents to skip
            
        Returns:
            Tuple containing:
            - List of documents for the requested page
            - Total count of all documents
        """
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

