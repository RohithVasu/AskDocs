FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN pip install uv

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN uv pip install -r requirements.txt

# Copy application code
COPY . .

# Create directories for document storage
RUN mkdir -p /app/data/documents /app/data/vectors

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose ports
EXPOSE 8000 8501

# Start both FastAPI and Streamlit services
CMD uv run "uv run --app app.main:app --reload --port 8000 & streamlit run app/frontend/app.py --server.port 8501 --server.address 0.0.0.0" --shell
