import json
import logging
import numpy as np

from datetime import datetime, timezone
from pathlib import Path
from app import config
from app.services.protocols import Embedder, TranscriptChunker, TranscriptFetcher, Repository
from app.storage.db import create_db_and_tables
from app.storage.models import Document
from app.storage.models import Chunk as DBChunk
from app.chunking.chunk import Chunk
from app.youtube.data_loader import Video, load_videos
from app.embedding.embed import get_sentence_transformer_embedder
from app.youtube.fetcher import YouTubeTranscriptFetcherWithCache
from app.youtube.transform import TranscriptSentencesChunker
from app.storage.repository import NativeMariadDBRepository

logger = logging.getLogger(__name__)


class VideoProcessingService:
    def __init__(
            self, repo: Repository, 
            transcript_fetcher: TranscriptFetcher, 
            transcript_chunker: TranscriptChunker, 
            embedder: Embedder,
        ):
        self.repo = repo
        self.transcript_fetcher = transcript_fetcher
        self.transcript_chunker = transcript_chunker
        self.embedder = embedder

    def populate_default_videos(self, drop_db_first: bool = False):
        logger.info("Creating database and tables")
        create_db_and_tables(drop_db_first=drop_db_first)

        videos = load_videos()

        logger.info(f"Processing {len(videos)} videos")

        for video in videos:
            logger.info(f"Processing video {video.id}")
            self.process_video(video)


    def process_video(self, video: Video):
        if self.repo.is_document_exists(video.url):
            logger.info(f"Document {video.id} already exists, skipping")
            return

        logger.info("Document doesn ot exists, fetching transcript")
        transcript = self.transcript_fetcher.fetch(video.id)

        logger.info("Splitting text into chunks for future embedding")
        chunks = self.transcript_chunker.split_into_chunks(transcript)
        
        logger.info(f"Embedding {len(chunks)} chunks")
        vectors = self.embedder.embed_texts([chunk.text for chunk in chunks])
        logger.info(f"Embedded {len(chunks)} chunks")

        logger.info("Inserting document and chunks into database")
        doc = Document(
            title=video.title, 
            created_at=datetime.now(timezone.utc), 
            url=video.url,
            meta=video.meta,
        )

        self._insert_vectors(doc, chunks, vectors)

    def export_videos_as_json_file(self, file_path: Path):
        documents = self.repo.list_documents()
        videos = [
            Video(id=doc.url.split("=")[-1], title=doc.title, meta=doc.meta).model_dump()
            for doc in documents
        ]

        with open(file_path, "w") as f:
            json.dump(videos, f, indent=4)

    def _insert_vectors(self, doc: Document, chunks: list[Chunk], vectors: np.ndarray):
        document_id = self.repo.insert_document(doc)

        db_chunks = [
            DBChunk(
                chunk_index=i,
                start_ts=chunk.metadata.start_time,
                end_ts=chunk.metadata.end_time,
                text=chunk.text,
                document_id=document_id,
                embedding=vectors[i],
            )
            for i, chunk in enumerate(chunks)
        ]

        self.repo.insert_chunks(db_chunks)


def get_default_video_processing_service() -> VideoProcessingService:
    repository = NativeMariadDBRepository()
    embedder = get_sentence_transformer_embedder(config.EMBEDDING_MODEL)
    transcript_fetcher = YouTubeTranscriptFetcherWithCache()
    transcript_chunker = TranscriptSentencesChunker(embedder.get_model(), config.TOKENS_PER_CHUNK)

    return VideoProcessingService(repository, transcript_fetcher, transcript_chunker, embedder)