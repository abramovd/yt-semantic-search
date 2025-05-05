import pytest

from app.services.crud import VideoCRUD


@pytest.fixture
def crud_service(mock_repository):
    return VideoCRUD(mock_repository)

def test_get_video(crud_service, mock_repository):
    video_id = 1
    
    video = crud_service.get_video(video_id)
    
    mock_repository.get_document.assert_called_once_with(video_id)
    assert video.url == "https://www.youtube.com/watch?v=video123"
    assert video.title == "Test Video"
    assert video.meta == {"duration": "10:00"}

def test_list_videos(crud_service, mock_repository):
    videos = crud_service.list_videos()
    
    mock_repository.list_documents.assert_called_once()
    assert len(videos) == 1
    assert videos[0].title == "Test Video"
    assert videos[0].internal_id == 1
    assert videos[0].id == "video123"

def test_list_videos_paginated(crud_service, mock_repository):
    limit = 10
    offset = 0
    
    videos, total = crud_service.list_videos_paginated(limit, offset)
    
    mock_repository.list_documents_paginated.assert_called_once_with(limit, offset)
    assert len(videos) == 1
    assert total == 1
    assert videos[0].title == "Test Video"
