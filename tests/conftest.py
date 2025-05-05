import pytest
import numpy as np
from unittest.mock import Mock

from app.services.protocols import (
    Embedder,
    TranscriptChunker,
    TranscriptFetcher,
    Repository,
    ReadOnlyRepository
)
from app.chunking.chunk import Chunk, ChunkMetadata
from app.storage.models import SearchResultChunk


@pytest.fixture
def mock_embedder():
    """Create a mock that follows the Embedder Protocol."""
    embedder = Mock(spec=Embedder)
    embedder.embed_text.return_value = np.array([0.1, 0.2, 0.3])
    embedder.embed_texts.return_value = np.array([
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6]
    ])
    embedder.get_model.return_value = "model"
    return embedder


@pytest.fixture
def mock_transcript_chunker():
    """Create a mock that follows the TranscriptChunker Protocol."""
    chunker = Mock(spec=TranscriptChunker)
    chunks = [
        Chunk(
            text="Chunk 1",
            metadata=ChunkMetadata(start_time=0, duration=10)
        ),
        Chunk(
            text="Chunk 2",
            metadata=ChunkMetadata(start_time=10, duration=10)
        )
    ]
    chunker.split_into_chunks.return_value = chunks
    return chunker


@pytest.fixture
def mock_transcript_fetcher():
    """Create a mock that follows the TranscriptFetcher Protocol."""
    fetcher = Mock(spec=TranscriptFetcher)
    fetcher.fetch.return_value = {"text": "This is a transcript"}
    return fetcher


@pytest.fixture
def mock_readonly_repository():
    """Create a mock that follows the ReadOnlyRepository Protocol."""
    repo = Mock(spec=ReadOnlyRepository)
    
    document = Mock()
    document.id = 1
    document.url = "https://youtube.com/watch?v=video123"
    document.title = "Test Video"
    document.meta = {"duration": "10:00"}
    
    repo.list_documents.return_value = [document]
    repo.list_documents_paginated.return_value = ([document], 1)
    repo.get_document.return_value = document
    repo.is_document_exists.return_value = False
    
    return repo


@pytest.fixture
def mock_repository():
    """Create a mock that follows the Repository Protocol (which extends ReadOnlyRepository)."""
    repo = Mock(spec=Repository)
    
    # Document mock for consistent data
    document = Mock()
    document.id = 1
    document.url = "https://youtube.com/watch?v=video123"
    document.title = "Test Video"
    document.meta = {"duration": "10:00"}
    
    # ReadOnlyRepository methods
    repo.list_documents.return_value = [document]
    repo.list_documents_paginated.return_value = ([document], 1)
    repo.get_document.return_value = document
    repo.is_document_exists.return_value = False
    
    # Repository methods
    repo.insert_document.return_value = 1
    repo.search.return_value = [
        SearchResultChunk(
            id=1,
            chunk_index=1,
            text="Result chunk 1",
            document_title="Test Video",
            document_url="https://youtube.com/watch?v=video123",
            start_ts=0,
            end_ts=10,
            distance=0.95
        ),
        SearchResultChunk(
            id=2,
            chunk_index=2,
            text="Result chunk 2",
            document_title="Test Video",
            document_url="https://youtube.com/watch?v=video123",
            start_ts=10,
            end_ts=20,
            distance=0.85,
        ),
    ]
    
    return repo
