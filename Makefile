# Docker Compose file
COMPOSE_FILE = ops/docker-compose.yaml
PROJECT_NAME=askdocs

# Base Compose command
DC=docker compose -p $(PROJECT_NAME) -f $(COMPOSE_FILE)

# Build the images (no start)
build:
	$(DC) build

# Build images from scratch (no cache)
build-nc:
	$(DC) build --no-cache

# Start services (does not rebuild images)
up:
	$(DC) up -d

# Start services and rebuild if needed
up-build:
	$(DC) up --build -d
	docker image prune -f

# Start dependencies only
up-deps:
	$(DC) up -d postgres pgadmin qdrant redis redis-worker

# Start backend only
up-backend:
	$(DC) up -d backend

# Stop services (but keep containers, volumes, and network)
stop:
	$(DC) stop

# Restart services
restart:
	$(MAKE) stop
	$(MAKE) up

# Bring everything down (containers, networks)
down:
	$(DC) down

# Bring everything down and remove volumes and orphans
nuke:
	$(DC) down --volumes --remove-orphans

# View logs
logs:
	$(DC) logs -f

# Show status
ps:
	$(DC) ps