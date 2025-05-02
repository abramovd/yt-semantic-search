import logging

from app import config
from app.services.protocols import Repository, Embedder
from app.storage.models import SearchResultChunk
from app.storage.repository import NativeMariadDBRepository
from app.embedding.embed import get_sentence_transformer_embedder

logger = logging.getLogger(__name__)

class VideoSearchService:
    def __init__(self, repo: Repository, embedder: Embedder):
        self.repo = repo
        self.embedder = embedder

    def search(self, query: str, num_neighbors: int = config.NUM_SEARCH_NEIGHBORS) -> list[SearchResultChunk]:
        query_vector = self.embedder.embed_text(query)
        return self.repo.search(query_vector, num_neighbors=num_neighbors)

def get_default_video_search_service() -> VideoSearchService:
    repository = NativeMariadDBRepository()
    embedder = get_sentence_transformer_embedder(config.EMBEDDING_MODEL)
    return VideoSearchService(repository, embedder)