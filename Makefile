# Image name
IMAGE_NAME = askdocs

# Default port exposed by Streamlit
PORT = 8501

# Build the Docker image
build:
	docker build -t $(IMAGE_NAME) -f ops/Dockerfile .

# Run the Docker container with env variable
run:
	@if [ ! -f .env ]; then \
		echo "Error: .env file not found."; \
		exit 1; \
	fi
	docker run --env-file .env --name $(IMAGE_NAME) -p $(PORT):8501 $(IMAGE_NAME)

# Remove the Docker image
clean:
	docker rmi $(IMAGE_NAME) || true

# Full rebuild
rebuild: clean build
