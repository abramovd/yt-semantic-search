import logging
import sys
from app.youtube.fetcher import fetch_video_transcript_with_cache
from app.youtube.transform import restore_punctuation_with_context
from app.embedding.embed import embed_texts
from app.storage.db import create_db_and_tables

def setup_logging():
    handler = logging.StreamHandler(sys.stdout)

    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s")
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    root_logger.addHandler(handler)


video_id = "XVcRQ6T9RHo"

if __name__ == "__main__":
    setup_logging()
    create_db_and_tables()
    transcript = fetch_video_transcript_with_cache(video_id)
    chunks = restore_punctuation_with_context(transcript)
    
    embeddings = embed_texts([chunk.text for chunk in chunks])
    print(embeddings.shape)
    print(embeddings[0])
