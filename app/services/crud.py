from pydantic import BaseModel
from typing import Tuple, List

from app.youtube.data_loader import Video
from app.services.protocols import ReadOnlyRepository
from app.services.video_processing import (
    VideoProcessingService, 
    get_default_video_processing_service,
)
from app.storage.repository import NativeMariadDBRepository

class VideoCRUD:
    def __init__(self, repository: ReadOnlyRepository):
        self.repository = repository

    def get_video(self, video_id: int):
        document = self.repository.get_document(video_id)
        return Video(id=str(document.id), url=document.url, title=document.title, meta=document.meta)

    def list_videos(self):
        """Legacy method for backwards compatibility."""
        documents = self.repository.list_documents()
        return [
            Video(
                internal_id=document.id,
                id=document.url.split("=")[-1], 
                title=document.title, 
                meta=document.meta,
            ) 
            for document in documents
        ]
        
    def list_videos_paginated(self, limit: int, offset: int) -> Tuple[List[Video], int]:
        """
        List videos with pagination.
        
        Args:
            limit: Maximum number of videos to return
            offset: Number of videos to skip
            
        Returns:
            Tuple containing:
            - List of videos for the requested page
            - Total count of all videos
        """
        documents, total_count = self.repository.list_documents_paginated(limit, offset)
        videos = [
            Video(
                internal_id=document.id,
                id=document.url.split("=")[-1], 
                title=document.title, 
                meta=document.meta,
            ) 
            for document in documents
        ]
        return videos, total_count

def get_default_video_crud() -> VideoCRUD:
    repository = NativeMariadDBRepository()
    return VideoCRUD(repository)
