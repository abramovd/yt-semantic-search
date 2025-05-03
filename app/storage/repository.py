import json
from typing import Tuple

import numpy as np
from app.storage.models import Document, Chunk, SearchResultChunk
from app.storage.db import native_connection


class NativeMariadDBRepository:
    def __init__(self):
        self.connection = native_connection()

    def insert_document(self, document: Document) -> int:
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO semantic_search.documents (title, url, created_at, meta) VALUES (%s, %s, %s, %s)",
            (document.title, document.url, document.created_at, json.dumps(document.meta))
        )
        self.connection.commit()
        return cursor.lastrowid
    
    def insert_chunk(self, chunk: Chunk):
        self.connection.cursor().execute(
            "INSERT INTO semantic_search.chunks (start_ts, end_ts, text, document_id, embedding) VALUES (%s, %s, %s, %s, %s)",
            (chunk.start_ts, chunk.end_ts, chunk.text, chunk.document_id, chunk.embedding)
        )
        self.connection.commit()

    def insert_chunks(self, chunks: list[Chunk]):
        self.connection.cursor().executemany(
            "INSERT INTO semantic_search.chunks (chunk_index, start_ts, end_ts, text, document_id, embedding) VALUES (%s, %s, %s, %s, %s,  VEC_FromText(%s))",
            [(chunk.chunk_index, chunk.start_ts, chunk.end_ts, chunk.text, chunk.document_id, str(chunk.embedding.tolist())) for chunk in chunks]
        )
        self.connection.commit()

    def is_document_exists(self, url: str) -> bool:
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM semantic_search.documents WHERE url = %s",
            (url,)
        )
        return cursor.fetchone()[0] > 0

    def search(self, query_vector: np.ndarray, num_neighbors: int = 5) -> list[SearchResultChunk]:
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(
        """
        SELECT chunk_index, start_ts, end_ts, text, document_id,
               VEC_DISTANCE_EUCLIDEAN(embedding, VEC_FromText(%s)) as distance,
               documents.title as document_title,
               documents.url as document_url
        FROM semantic_search.chunks
        JOIN semantic_search.documents ON chunks.document_id = documents.id
        ORDER BY distance ASC
        LIMIT %s;
        """,
            (str(query_vector.tolist()), num_neighbors)
        )
        result = cursor.fetchall()
        return [SearchResultChunk(**row) for row in result]
    
    def list_documents(self) -> list[Document]:
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT id, title, created_at, url, meta FROM semantic_search.documents")
        return [_dict_to_document(row) for row in cursor.fetchall()]
    
    def list_documents_paginated(self, limit: int, offset: int) -> Tuple[list[Document], int]:
        """List documents with pagination."""
        # First, get the total count
        count_cursor = self.connection.cursor()
        count_cursor.execute("SELECT COUNT(*) FROM semantic_search.documents")
        total_count = count_cursor.fetchone()[0]
        
        # Then get the paginated results
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, title, created_at, url, meta FROM semantic_search.documents ORDER BY id LIMIT %s OFFSET %s",
            (limit, offset)
        )
        
        documents = [_dict_to_document(row) for row in cursor.fetchall()]
        return documents, total_count
    
    def get_document(self, document_id: int) -> Document:
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT id, title, created_at, url, meta FROM semantic_search.documents WHERE id = %s", (document_id,))
        return _dict_to_document(cursor.fetchone())


def _dict_to_document(row: dict) -> Document:
    row["meta"] = json.loads(row["meta"])
    return Document(**row)