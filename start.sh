# #!/bin/bash

# #Activate virtual environment
# echo "Activating virtual environment..."
# uv sync
# source .venv/bin/activate

# # Check for required environment variables
# if [ -z "$ASKDOCS_LLM_API_KEY" ]; then
#     echo "Error: ASKDOCS_LLM_API_KEY environment variable is not set"
#     echo "Please set ASKDOCS_LLM_API_KEY before running the application"
#     exit 1
# fi

# #Pull values from env variables or hardcoded config
# HOST=$(python -c "from app.core.settings import settings; print(settings.fastapi.host)")
# PORT=$(python -c "from app.core.settings import settings; print(settings.fastapi.port)")

# # Start backend server
# echo "Starting backend server on $HOST:$PORT..."
# uvicorn app.backend.main:app --host "$HOST" --port "$PORT" --reload --reload-dir ./app/backend --reload-exclude ./app/frontend &

# # Start frontend in a new terminal
# if [[ "$OSTYPE" == "darwin"* ]]; then
#     # macOS
#     osascript -e 'tell app "Terminal" to do script "cd ""'"$PWD"'" && PYTHONPATH=. streamlit run app/frontend/main.py"'
# else
#     # Linux
#     gnome-terminal -- bash -c "cd "$PWD" && PYTHONPATH=. streamlit run app/frontend/main.py"
# fi

# # Wait for both processes to finish
# wait


#!/bin/bash

# Activate virtual environment
echo "Activating virtual environment..."
uv sync
source .venv/bin/activate

# Check for required environment variables
if [ -z "$ASKDOCS_LLM_API_KEY" ]; then
    echo "Error: ASKDOCS_LLM_API_KEY environment variable is not set"
    echo "Please set ASKDOCS_LLM_API_KEY before running the application"
    exit 1
fi

# Pull values from env variables or hardcoded config
HOST=$(python -c "from app.core.settings import settings; print(settings.fastapi.host)")
PORT=$(python -c "from app.core.settings import settings; print(settings.fastapi.port)")

# Start backend server in background
echo "Starting backend server on $HOST:$PORT..."
PYTHONPATH=. uvicorn app.backend.main:app \
  --host "$HOST" \
  --port "$PORT" \
  --reload \
  --reload-dir ./app/backend \
  --reload-exclude ./app/frontend \
  > backend.log 2>&1 &

BACKEND_PID=$!

# Start frontend (Streamlit) in background
echo "Starting frontend (Streamlit)..."
PYTHONPATH=. streamlit run app/frontend/main.py > frontend.log 2>&1 &

FRONTEND_PID=$!

# Wait for both processes
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
wait $BACKEND_PID $FRONTEND_PID
