import os

PUNC_MODEL = "oliverguhr/fullstop-punctuation-multilang-large"
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
TOKENS_PER_CHUNK = os.getenv("TOKENS_PER_CHUNK", 150)
NUM_SEARCH_NEIGHBORS = os.getenv("NUM_SEARCH_NEIGHBORS", 5)

DB_USERNAME = os.getenv("DB_USER", "app_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Password123!")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = os.getenv("DB_NAME", "semantic_search")
