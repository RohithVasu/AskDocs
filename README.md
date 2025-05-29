# AskDocs

**AskDocs** is an intelligent application that allows users to upload and index a variety of document formats—including PDF, DOCX, PPT, and CSV—and interact with the content through natural language conversations.

**Key Features**:
- **📄 Multi-format Support**: Upload and index DOCX, PDF, PPT, and CSV files
- **💬 Conversational AI**: Ask questions about document content and get accurate, context-aware answers
- **🚀 Fast & Scalable Search**: Uses vector databases for semantic search and retrieval
- **🧠 Memory & Context**: Understands multi-turn conversations for deeper insights
- **🔐 Secure & Extensible**: Built with privacy and modularity in mind

**Powered by cutting-edge AI technologies**:
- **LLM (Large Language Models)**: For natural language understanding and generation
- **LangChain**: For enhanced document processing and retrieval
- **Vector Search**: For semantic search capabilities

This tool transforms static documents into interactive knowledge sources. Whether it's reports, contracts, spreadsheets, or research papers, you can now ask questions, summarize, extract insights, and explore data contextually—as if you were chatting with a human expert.

## Prerequisites

- **[Python](https://www.python.org/)**: Version 3.12 or higher
- **[uv](https://docs.astral.sh/uv/getting-started/installation/)**: Package manager for python
- **[Docker](https://docs.docker.com/get-started/get-docker/)**: For containerizing and running the application in isolated environments
- **[Make](https://www.gnu.org/software/make)**: For using Makefile commands


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
make build
make run
```

### Local Installation

1. Set up environment variables:
Create a `.env` file with:
```
ASKDOCS_LLM_API_KEY=your_api_key_here
```

2. Run the application:
```bash
./start.sh
```

