.PHONY: build up down logs ps clean

# Build the containers
build:
	docker-compose build

# Start the containers in detached mode
up:
	docker-compose up -d

# Stop the containers
down:
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# Show running containers
ps:
	docker-compose ps

# Clean up containers, volumes, and images
clean:
	docker-compose down -v
	docker system prune -f

# Start the application (build + up)
start: build up

# Restart the application
restart: down up

# Show logs for a specific service (usage: make service-logs SERVICE=app)
service-logs:
	docker-compose logs -f $(SERVICE) 