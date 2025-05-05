# YouTube Semantic Search

A semantic search application for YouTube videos based on captions.

## Features

- Process YouTube videos and extract captions
- Create semantic embeddings for video content
- Search for specific topics within videos using natural language
- Web UI with Gradio
- Command-line interface with Typer


<img src="https://vhs.charm.sh/vhs-6q16oujtXo3N0OAQJJPQJp.gif">


## Architecture

This project demonstrates integration between:
- **MariaDB** for data storage (specifically Vector type column for each video chunk)
- **Python** for backend processing: data extraction, data cleanup, running ML models and building user interfaces:
    - [transformers](https://github.com/huggingface/transformers) library for running HuggingFace models locally
        - Used for punctuation and embedding models
    - [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) for caption retrieval
    - [typer](https://github.com/fastapi/typer) for CLI and [gradio](https://github.com/gradio-app/gradio) for WebUI
    - [NLTK](https://github.com/nltk/nltk) for processing YouTube caption snippets (splitting into sentences)
    

## Implementation

The main currently tested use case is semantic search of YouTube videos about Python (from different PyCon conferences).
The primary data source for the search is auto-generated YouTube captions.

The system is implemented as a set of well-defined components:

### 1. Data Population

See the main business logic for processing new videos under `app/services/video_processing.py`

1. Collecting captions from a specific subset of YouTube videos (Python-related conferences like PyCon)
    - See `app/youtube/fetcher`
    - To avoid hitting YouTube rate limits, [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) caches captions as pickle objects locally under the `data/` folder (git ignored) and reuses them on subsequent runs
    - As an example, a small curated list of Python YouTube videos for database population can be found at `app/youtube/youtube_videos.json`.
  
2. Prepare the captions for future embedding:
    - See `app/youtube/transform` and `app/chunking`
    - Restore missing punctuation from caption snippets using a dedicated punctuation model (`oliverguhr/fullstop-punctuation-multilang-large`)
    - After adding punctuation, split the text into sentences
    - Chunk the data by a configurable number of tokens per chunk by combining full sentences. This allows us to group only contextually related data (by sentences) together
    - Each final chunk maintains the context of which video [start-timestamp; end-timestamp] interval it belongs to

3. Run the embedding model on the chunks to get vector representation
    - See `app/embedding` for more implementatiion details
    - By default, using `all-MiniLM-L6-v2` model for vector embedding

4. Insert each vectorized video chunk into MariaDB Vector store alongside its context (video information, start and end timestamps, etc.)
    - See `app/storage` for more implementatiion details
    - Currently `Euclidean` distance vector is used
    - `Cosine` distance metric showed similar performance

### 2. Search Query Executor

See the main business logic for processing search queries against embedded YouTube video captions under `app/services/search`.

- Vectorize natural language query using the same embedding model as when populating the data
- Find N nearest neighbors by `Euclidean` distance score between vectorized query and existing vectors of chunks
- Find and output N closest video chunks for the provided query

### 3. APIs for Working with Chunked and Vectorized Video Documents

See `app/service/crud.py` for the business logic implementation of working with data from the MariaDB database.

### 4. Clients

- Command Line Tool to populate / query / manage data
- Web Frontend to query and view data with working links to YouTube videos

## Setup Instructions

- Python 3.13+
- MariaDB 11.7+
- Docker and Docker Compose (optional, for containerized setup)

### Using Docker (recommended) - Web UI

1. Build and start the application with Docker Compose:
   ```
   make up
   ```

2. The application will be available at:
   - Web UI: http://localhost:7860

### Running Locally Without Docker (CLI)

1. Install Python 3.13+
2. [Install uv](https://docs.astral.sh/uv/getting-started/installation/) for dependency management 
3. [Install MariaDB Connector C](https://mariadb.com/docs/server/connect/programming-languages/c/install/)
4. Have MariaDB running (e.g., from existing docker-compose.yml)
5. Install required dependencies:
   ```
   uv sync
   ```
6. Configure environment variables if needed (see Configuration section)
7. Run the application:
   ```
   uv run -m app.cli
   ```

## Configuration

The application can be configured using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| DB_USER | Database username | app_user |
| DB_PASSWORD | Database password | Password123! |
| DB_HOST | Database hostname | 127.0.0.1 |
| DB_PORT | Database port | 3306 |
| DB_NAME | Database name | semantic_search |
| EMBEDDING_MODEL | Hugging Face model for embeddings | all-MiniLM-L6-v2 |

## Usage

### Command Line Interface

The application provides a CLI for common operations:

```bash
# Populate the database with default videos
uv run -m app.cli video populate

# Search videos
uv run -m app.cli video search "your search query"

# List all videos
uv run -m app.cli video list

# Add a new video
uv run -m app.cli video create --id YOUTUBE_VIDEO_ID --title "Video Title" --metadata "{}"
```

### Web UI

The Gradio web UI provides a user-friendly interface with:
- Video list with pagination
- Search functionality
- Result visualization

## Development

This project uses a modular architecture with clear separation of concerns:
- `app/services`: Business logic
- `app/storage`: Data persistence (using Maria DB)
- `app/youtube`: YouTube data fetching and processing
- `app/chunking`: Text chunking for embeddings
- `app/embedding`: Vector embeddings generation

## Testing

This project uses pytest for testing. Tests are organized to match the application structure:

- `tests/services`: Tests for business logic services with protocol stubs
- Additional test directories will be added as needed

### Running Tests

You can run tests using the included `make` commands:

```bash
# Run all tests
make test

# Run linter or auto fixes for linting
make lint
make lint-fix
```

Tests are designed to use protocol stubs, leveraging Python's duck typing and Protocol classes to ensure correct interfaces without needing actual implementations during testing.

## Planned Future Improvements

- Public HTTP API using FastAPI
- Scripts for automatically extracting YouTube videos for specific topics (like PyCon conferences in this case)
- More UI features
- More experiments with different embedding models and chunking techniques
- Experiment with using Python ORMs for working with MariaDB (`SQLModel`, `SQLAlchemy`) instead of raw queries and `alembic` for database migrations

## License

This project is licensed under the MIT License - a permissive license that is short and to the point. It lets people do almost anything they want with your project, like making and distributing closed source versions, as long as they provide attribution back to you and don't hold you liable.

Copyright (c) 2025 Dmytro Abramov

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files, to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software.
