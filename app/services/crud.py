from pydantic import BaseModel

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
        documents = self.repository.list_documents()
        return [
            Video(id=str(document.id), url=document.url, title=document.title, meta=document.meta) 
            for document in documents
        ]

def get_default_video_crud() -> VideoCRUD:
    repository = NativeMariadDBRepository()
    return VideoCRUD(repository)
