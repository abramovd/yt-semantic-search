from typing import List
from transformers import PreTrainedTokenizer
from nltk import sent_tokenize

class ChunkMetadata:
    def __init__(self, start_time: float, duration: float):
        self.start_time = start_time
        self.end_time = self.start_time + duration

    @property
    def duration(self):
        return self.end_time - self.start_time

    def __str__(self):
        return f"ChunkMetadata(start_time={self.start_time}, end_time={self.end_time}, duration={self.duration})"

class Chunk:
    def __init__(self, text: str, metadata: ChunkMetadata):
        self.text = text
        self.metadata = metadata

    def merge(self, other: 'Chunk') -> 'Chunk':
        start_time = self.metadata.start_time if self.metadata.start_time else other.metadata.start_time 
        metadata = ChunkMetadata(
            start_time,
            other.metadata.end_time - start_time,
        )
        return Chunk(self.text.strip() + " " + other.text.strip(), metadata)
    
    def __str__(self):
        return f"Chunk(text={self.text}, metadata={self.metadata})"

def chunk_by_sentence(text: str) -> List[str]:
    return sent_tokenize(text)


def merge_chunks_by_tokenizer(
    chunks: List[Chunk],
    tokenizer: PreTrainedTokenizer,
    max_tokens: int = None,
    separator: str = " "
) -> list[Chunk]:
    if max_tokens is None:
        max_tokens = tokenizer.model_max_length
    sep_token_count = len(tokenizer.tokenize(separator))
    max_tokens = min(max_tokens, tokenizer.model_max_length)
    merged_chunks = []
    current_chunk = Chunk("", ChunkMetadata(0, 0))
    current_token_count = 0
    for chunk in chunks:
        chunk_token_count = len(tokenizer.tokenize(chunk.text))
        if current_token_count + sep_token_count + chunk_token_count <= max_tokens:
            current_chunk = current_chunk.merge(chunk)
            current_token_count += sep_token_count + chunk_token_count
        else:
            merged_chunks.append(current_chunk)
            current_chunk = chunk
            current_token_count = chunk_token_count
    merged_chunks.append(current_chunk)
    return merged_chunks 

def merge_text_chunks_by_tokenizer(
    chunks: list[str],
    tokenizer: PreTrainedTokenizer,
    max_tokens: int = None,
    separator: str = " "
) -> list[str]:
    if max_tokens is None:
        max_tokens = tokenizer.model_max_length
    sep_token_count = len(tokenizer.tokenize(separator))
    max_tokens = min(max_tokens, tokenizer.model_max_length)
    merged_chunks = []
    current_chunk = ""
    current_token_count = 0
    for chunk in chunks:
        chunk_token_count = len(tokenizer.tokenize(chunk))
        if current_token_count + sep_token_count + chunk_token_count <= max_tokens:
            current_chunk += chunk + separator
            current_token_count += sep_token_count + chunk_token_count
        else:
            merged_chunks.append(current_chunk.strip())
            current_chunk = chunk
            current_token_count = chunk_token_count
    merged_chunks.append(current_chunk.strip())
    return merged_chunks