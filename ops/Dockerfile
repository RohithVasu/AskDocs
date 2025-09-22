FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy all project files
COPY . /app

# Install the application dependencies
WORKDIR /app
RUN uv sync --frozen --no-cache

# Set dynaconf environment for production
ENV ENV_FOR_DYNACONF=production

# Run the custom start script
CMD ["bash", "start.sh"]