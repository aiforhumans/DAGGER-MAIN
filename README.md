# Dagger CLI with Docker Model Runner (DMR) + Gemma 3

This project demonstrates how to wire Dagger CLI to Docker Model Runner using Gemma 3 as the default AI model.

## Prerequisites

- **Docker Desktop** with Model Runner enabled
- **Windows/NVIDIA** is supported
- **Dagger CLI** installed

## Setup Instructions

### 1. Enable Docker Model Runner

```powershell
# Enable Docker Model Runner with optional TCP access on port 12434
docker desktop enable model-runner --tcp 12434
```

### 2. Pull Gemma 3 Model

```powershell
# Pull the Gemma 3 model into Docker Model Runner
docker model pull ai/gemma3
```

Verify the model is available:
```powershell
docker model ls
```

You should see `ai/gemma3:latest` in the list.

### 3. Configure Environment Variables

The `.env` file in this directory is already configured with:

```env
# Docker Model Runner configuration
OPENAI_BASE_URL=http://model-runner.docker.internal/engines/v1/
OPENAI_MODEL=index.docker.io/ai/gemma3
OPENAI_DISABLE_STREAMING=true
DMR_API_KEY="anything"
DMR_BASE_MODEL="ai/gemma3"
```

**Key Points:**
- `OPENAI_BASE_URL` points to DMR's OpenAI-compatible endpoint from inside containers
- `OPENAI_MODEL` specifies Gemma 3 as the default model
- `OPENAI_DISABLE_STREAMING` is recommended with llama.cpp backend used by DMR

## Usage

### Test the Configuration

1. **Check which model Dagger will use:**
   ```powershell
   dagger -c 'llm | model'
   ```
   Expected output: `index.docker.io/ai/gemma3`

2. **Get a response from Gemma 3:**
   ```powershell
   dagger -c 'llm | with-prompt "Reply with: hello from Gemma3" | last-reply'
   ```

### Common Dagger LLM Commands

```powershell
# Check current model
dagger -c 'llm | model'

# Force a specific model
dagger -c 'llm | with-model "index.docker.io/ai/gemma3" | with-prompt "Your prompt here" | last-reply'

# Interactive LLM session
dagger -c 'llm | with-prompt "Explain what Docker is" | last-reply'
```

## API Endpoints

- **From containers (Dagger Engine):** `http://model-runner.docker.internal/engines/v1`
- **From host (if TCP enabled):** `http://localhost:12434/engines/v1`
- **Engine-specific path:** `/engines/llama.cpp/v1` (optional, defaults to llama.cpp)

## Troubleshooting

### Model Not Found
```powershell
# Check available models
docker model ls

# Pull Gemma 3 if missing
docker model pull ai/gemma3
```

### Connection Issues
- Ensure Docker Desktop is running with Model Runner enabled
- Verify the `.env` file is in your working directory
- Check that `OPENAI_BASE_URL` uses `model-runner.docker.internal` (for container access)

### Dagger Issues
```powershell
# Check Dagger version
dagger version

# Verify environment variables are loaded
dagger -c 'llm | model'
```

## References

- [Docker Model Runner Documentation](https://docs.docker.com/desktop/model-runner/)
- [Dagger LLM Documentation](https://docs.dagger.io/features/llm/)
- [Docker Gemma 3 Guide](https://docs.docker.com/guides/use-cases/genai-llm-model-runner/)
- [Dagger + DMR Blog Post](https://dagger.io/blog/ai-development-docker-model-runner)

## Notes

- Dagger automatically picks up environment variables from your shell or local `.env` file
- The LLM shell fields use hyphenated syntax: `model`, `with-model`, `with-prompt`, `last-reply`
- Streaming is disabled for better compatibility with llama.cpp backend