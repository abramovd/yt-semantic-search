import pytest

from app.services.search import VideoSearchService


@pytest.fixture
def service(mock_repository, mock_embedder):
    return VideoSearchService(mock_repository, mock_embedder)

def test_search(service, mock_repository, mock_embedder):
    query = "test query"
    num_neighbors = 5
    
    results = service.search(query, num_neighbors)
    
    mock_embedder.embed_text.assert_called_once_with(query)
    mock_repository.search.assert_called_once()
    assert len(results) == 2
    assert results[0].text == "Result chunk 1"
    assert results[0].distance == 0.95
    assert results[1].text == "Result chunk 2"
    assert results[1].distance == 0.85
