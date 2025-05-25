# Document Chat Application

A production-ready application that allows users to index various document types (DOCX, Excel, CSV, PDF) and chat with them using AI.

## Features

- Support for multiple document formats (DOCX, Excel, CSV, PDF)
- Document indexing and vector storage
- AI-powered chat interface
- FastAPI backend with REST API
- Streamlit frontend interface
- Docker support for easy deployment

## Installation

### Using Docker (Recommended)

```bash
docker build -t doc-chat .
docker run -p 8501:8501 -p 8000:8000 doc-chat
```

### Local Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
Create a `.env` file with:
```
OPENAI_API_KEY=your_api_key_here
```

3. Run the application:
```bash
# Start FastAPI server
uvicorn app.main:app --reload --port 8000

# Start Streamlit interface in another terminal
streamlit run app/frontend/app.py
```

## Usage

1. Upload documents through the Streamlit interface
2. Ask questions about the uploaded documents
3. Get AI-powered responses based on the document content

## API Documentation

The FastAPI server provides the following endpoints:

- `POST /upload` - Upload documents
- `POST /chat` - Chat with documents
- `GET /health` - Health check endpoint

## Supported Document Types

- Microsoft Word (.docx)
- Microsoft Excel (.xlsx)
- CSV (.csv)
- PDF (.pdf)

## Project Structure

```
.
├── app/
│   ├── backend/         # FastAPI backend
│   │   ├── main.py      # API endpoints
│   │   ├── models.py    # Pydantic models
│   │   └── utils.py     # Utility functions
│   └── frontend/        # Streamlit frontend
│       └── app.py       # Streamlit interface
├── config/              # Configuration files
├── docker/              # Docker configuration
└── tests/              # Test files
```
