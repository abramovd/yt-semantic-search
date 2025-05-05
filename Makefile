.PHONY: build up down logs ps clean

build:
	docker-compose build

up:
	docker-compose up

# Stop the containers
down:
	docker-compose down

logs:
	docker-compose logs -f

# Clean up containers, volumes, and images
clean:
	docker-compose down -v
	docker system prune -f

# Start the application (build + up)
start: build up

# Restart the application
restart: down up

# Run tests (uses app service by default)
test:
	docker-compose run --rm app uv run pytest

lint:
	docker-compose run --rm app uv run ruff check .

lint-fix:
	docker-compose run --rm app uv run ruff check --fix .
