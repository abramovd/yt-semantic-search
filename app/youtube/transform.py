import logging

from copy import copy
from functools import lru_cache

from youtube_transcript_api import FetchedTranscript
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
from sentence_transformers import SentenceTransformer
from app import config
from app.chunking.chunk import (
    Chunk, ChunkMetadata, 
    chunk_by_sentence,
    merge_chunks_by_tokenizer, 
    merge_text_chunks_by_tokenizer,
)

logger = logging.getLogger(__name__)


class TranscriptSentencesChunker:
    """
    Split transcript into chunks by sentences. 
    As transcript does not have any punctuation, we need to restore it first.
    """
    def __init__(self, sentence_transformer: SentenceTransformer, tokens_per_chunk: int):
        self.sentence_transformer = sentence_transformer
        self.tokens_per_chunk = tokens_per_chunk

    def split_into_chunks(self, transcript: FetchedTranscript) -> list[Chunk]:
        return split_into_sentences_chunks(transcript, self.sentence_transformer, self.tokens_per_chunk)


@lru_cache
def get_punctuator():
    tok = AutoTokenizer.from_pretrained(config.PUNC_MODEL)
    model = AutoModelForTokenClassification.from_pretrained(config.PUNC_MODEL)
    punctuator = pipeline("ner", model=model, tokenizer=tok, aggregation_strategy="simple")
    return punctuator

def restore_punctuation(text: str) -> str:
    punctuated_tokens = get_punctuator()(text.lower())
    punctuated_text = ""
    for token in punctuated_tokens:
        word = token["word"]
        if token["entity_group"] in [".", ",", "!", "?", ";", ":"]:
            punctuated_text = punctuated_text.rstrip() + " "+ word + token["entity_group"]
        else:
            punctuated_text += " " + word

    return punctuated_text

def split_into_sentences_chunks(
    transcript: FetchedTranscript, 
    embedding_model: SentenceTransformer, 
    tokens_per_chunk: int
) -> list[Chunk]:
    chunks = [
        Chunk(snippet.text, ChunkMetadata(snippet.start, snippet.duration))
        for snippet in transcript.snippets
    ]

    # Merge chuns to run punctuation model on them
    merged_chunks = merge_chunks_by_tokenizer(chunks, get_punctuator().tokenizer)

    # Restore punctuation per chunk
    for chunk in merged_chunks:
        chunk.text = restore_punctuation(chunk.text)

    # Split whole text into sentences
    full_text = " ".join([chunk.text for chunk in merged_chunks])
    sentences = chunk_by_sentence(full_text)

    merged_sentences = merge_text_chunks_by_tokenizer(
        sentences, embedding_model.tokenizer, max_tokens=tokens_per_chunk,
    )

    # Enrich merged sentences with metadata from original transcript segments.
    num_chars = 0
    final_chunks = []
    tok = get_punctuator().tokenizer
    for sentence in merged_sentences:
        num_chars += len(tok.tokenize(sentence))
        original_chunk_num = num_chars // tok.model_max_length

        original_chunk = copy(merged_chunks[original_chunk_num])
        original_chunk.text = sentence
        
        final_chunks.append(original_chunk)

    return final_chunks
