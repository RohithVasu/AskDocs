#!/bin/bash

#Activate virtual environment
echo "Activating virtual environment..."
uv sync
source .venv/bin/activate

#Run the app
echo "Starting the app..."
uvicorn app.backend.main:app --reload