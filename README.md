# YouTube Semantic Search

A tool for semantically searching YouTube video content.

## Features

- Import YouTube videos into a searchable database
- Perform semantic search on video content
- Command-line interface with various commands
- Web interface for browsing and searching videos

## Installation

Ensure you have Python 3.13+ installed.

```bash
# Clone the repository
git clone https://github.com/abramovd/yt-semantic-search.git
cd yt-semantic-search

# Install dependencies
pip install -e .
```

## Usage

### Command Line Interface

```bash
# Populate the database with default videos
python -m app.cli video populate

# List all videos in the database
python -m app.cli video list

# Search for videos
python -m app.cli video search "your search query"
```

### Web Interface (Gradio)

The application provides a web interface using Gradio for easier interaction:

```bash
# Start the web interface
python run_frontend.py
```

This will start a server at http://localhost:7860 where you can:

1. Browse all available videos with thumbnails
2. Search videos using semantic search
3. Click on search results to watch videos at specific timestamps

## Dependencies

- MariaDB with vector extensions for semantic search
- Sentence Transformers for embedding generation
- Gradio for the web interface
- Typer for the command-line interface
