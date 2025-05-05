# YouTube Semantic Search

A semantic search application for YouTube videos based on captions.

## Features

- Process YouTube videos and extract captions
- Create semantic embeddings for video content
- Search for specific topics within videos using natural language
- Web UI with Gradio
- Command-line interface with Typer

## Architecture

This project demonstrates integration between:
- **MariaDB** for data storage
- **Python** for backend processing
- **AI/ML** for semantic search capabilities

## Requirements

- Python 3.13+
- MariaDB 11.7+
- Docker and Docker Compose (optional, for containerized setup)

## Setup Instructions

### Using Docker (recommended)

1. Build and start the application with Docker Compose:
   ```
   docker-compose up -d
   ```

2. The application will be available at:
   - Web UI: http://localhost:7860
   - API Documentation: http://localhost:8000/docs (if FastAPI is implemented)

### Manual Setup

1. Install Python 3.13+
2. Install required dependencies:
   ```
   uv pip install -e .
   ```
3. Configure environment variables (see Configuration section)
4. Run the application:
   ```
   python -m app.cli
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
python -m app.cli video populate

# Search videos
python -m app.cli video search "your search query"

# List all videos
python -m app.cli video list

# Add a new video
python -m app.cli video create --id VIDEO_ID --title "Video Title"
```

### Web UI

The Gradio web UI provides a user-friendly interface with:
- Video list with pagination
- Search functionality
- Result visualization

## Development

This project uses a modular architecture with clear separation of concerns:
- `app/services`: Business logic
- `app/storage`: Data persistence
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

# Run tests with coverage report
make test-coverage
```

Tests are designed to use protocol stubs, leveraging Python's duck typing and Protocol classes to ensure correct interfaces without needing actual implementations during testing.

## Continuous Integration

This project uses GitHub Actions for continuous integration. The CI pipeline runs automatically on:
- Pull requests to the main branch
- Pushes to the main branch

The CI workflow:
1. Builds the Docker containers
2. Runs linting checks with `make lint`
3. Runs tests with `make test`

Pull requests cannot be merged unless the linting and tests pass successfully.

## License

[Add your license information here]
