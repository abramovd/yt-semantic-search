import pytest

from app.services.video_processing import VideoProcessingService
from app.youtube.data_loader import Video



@pytest.fixture
def service(mock_repository, mock_transcript_fetcher, mock_transcript_chunker, mock_embedder):
    return VideoProcessingService(
        mock_repository,
        mock_transcript_fetcher,
        mock_transcript_chunker,
        mock_embedder
    )

def test_process_video_new_document(
    service, mock_repository, mock_transcript_fetcher, mock_transcript_chunker, mock_embedder,
):
    video = Video(id="video123", url="https://youtube.com/watch?v=video123", title="Test Video", meta={})
    service.process_video(video)
    mock_transcript_fetcher.fetch.assert_called_once_with("video123")
    mock_transcript_chunker.split_into_chunks.assert_called_once()
    mock_embedder.embed_texts.assert_called_once()
    mock_repository.insert_document.assert_called_once()
    mock_repository.insert_chunks.assert_called_once()

def test_process_video_existing_document(service, mock_repository):
    video = Video(id="video123", url="https://youtube.com/watch?v=video123", title="Test Video", meta={})
    mock_repository.is_document_exists.return_value = True
    
    service.process_video(video)
    
    mock_repository.is_document_exists.assert_called_once_with(video.url)
    mock_repository.insert_document.assert_not_called()
    mock_repository.insert_chunks.assert_not_called()
