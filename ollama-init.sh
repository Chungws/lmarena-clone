#!/bin/bash
# Ollama initialization script
# Automatically downloads specified models on container startup

set -e

echo "=========================================="
echo "Ollama Initialization Script"
echo "=========================================="

# Start Ollama server in the background
echo "[INFO] Starting Ollama server..."
/bin/ollama serve &
OLLAMA_PID=$!

# Wait for Ollama server to be ready
echo "[INFO] Waiting for Ollama server to be ready..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if ollama list > /dev/null 2>&1; then
        echo "[SUCCESS] Ollama server is ready!"
        break
    fi
    attempt=$((attempt + 1))
    echo "[INFO] Attempt $attempt/$max_attempts - Ollama not ready yet, waiting 2 seconds..."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "[ERROR] Ollama server failed to start after $max_attempts attempts"
    exit 1
fi

# Download models if OLLAMA_MODELS is set
if [ -n "$OLLAMA_MODELS" ]; then
    echo "[INFO] Models to download: $OLLAMA_MODELS"

    # Split comma-separated models
    IFS=',' read -ra MODELS <<< "$OLLAMA_MODELS"

    for model in "${MODELS[@]}"; do
        # Trim whitespace
        model=$(echo "$model" | xargs)

        echo "=========================================="
        echo "[INFO] Checking model: $model"

        # Check if model already exists
        if ollama list | grep -q "$model"; then
            echo "[INFO] Model '$model' already exists, skipping download"
        else
            echo "[INFO] Downloading model: $model"
            if ollama pull "$model"; then
                echo "[SUCCESS] Model '$model' downloaded successfully"
            else
                echo "[WARNING] Failed to download model '$model', continuing..."
            fi
        fi
    done

    echo "=========================================="
    echo "[SUCCESS] Model initialization complete!"
    echo "=========================================="
else
    echo "[INFO] No models specified in OLLAMA_MODELS, skipping downloads"
fi

# List all available models
echo "[INFO] Available models:"
ollama list

echo "=========================================="
echo "[INFO] Ollama is ready to accept requests"
echo "=========================================="

# Keep the script running and forward signals to Ollama
wait $OLLAMA_PID
