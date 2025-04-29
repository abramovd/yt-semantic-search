import logging
from copy import copy
from nltk import sent_tokenize
from youtube_transcript_api import FetchedTranscript
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
from sentence_transformers import SentenceTransformer
from app.chunking.chunk import (
    Chunk, ChunkMetadata, 
    chunk_by_sentence,
    merge_chunks_by_tokenizer, 
    merge_text_chunks_by_tokenizer,
)
logger = logging.getLogger(__name__)

SENTENCES_CHUNK_SIZE = 150

PUNC_MODEL = "oliverguhr/fullstop-punctuation-multilang-large"
tok = AutoTokenizer.from_pretrained(PUNC_MODEL)
model = AutoModelForTokenClassification.from_pretrained(PUNC_MODEL)
punctuator = pipeline("ner", model=model, tokenizer=tok, aggregation_strategy="simple")

HF_MODEL = "all-MiniLM-L6-v2"
embed_tokenizer = SentenceTransformer(HF_MODEL).tokenizer


def full_text_from_transcript(transcript: FetchedTranscript) -> str:
    return " ".join(segment.text for segment in transcript.snippets)

def restore_punctuation(text: str) -> str:
    punctuated_tokens = punctuator(text.lower())
    punctuated_text = ""
    for token in punctuated_tokens:
        word = token["word"]
        if token["entity_group"] in [".", ",", "!", "?", ";", ":"]:
            punctuated_text = punctuated_text.rstrip() + " "+ word + token["entity_group"]
        else:
            punctuated_text += " " + word

    return punctuated_text

def restore_punctuation_with_context(transcript: FetchedTranscript) -> list[Chunk]:
    chunks = [
        Chunk(snippet.text, ChunkMetadata(snippet.start, snippet.duration))
        for snippet in transcript.snippets
    ]

    # Merge chuns to run punctuation model on them
    merged_chunks = merge_chunks_by_tokenizer(chunks, tok)

    # Restore punctuation per chunk
    for chunk in merged_chunks:
        chunk.text = restore_punctuation(chunk.text)

    # Split all text into sentences
    full_text = " ".join([chunk.text for chunk in merged_chunks])
    sentences = chunk_by_sentence(full_text)

    merged_sentences = merge_text_chunks_by_tokenizer(sentences, embed_tokenizer, max_tokens=SENTENCES_CHUNK_SIZE)

    # Enrich merged sentences with metadata from original transcript segments.
    num_chars = 0
    final_chunks = []
    for sentence in merged_sentences:
        num_chars += len(tok.tokenize(sentence))
        original_chunk_num = num_chars // tok.model_max_length

        original_chunk = copy(merged_chunks[original_chunk_num])
        original_chunk.text = sentence
        
        final_chunks.append(original_chunk)

    return final_chunks
