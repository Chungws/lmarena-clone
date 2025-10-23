# Models Configuration

This directory contains LLM model configuration templates.

## Available Templates

| File | Environment | Ollama URL | Use Case |
|------|-------------|------------|----------|
| **models.dev.yaml** | Development | `http://localhost:11434/v1` | Local development with Ollama on host |
| **models.prod.yaml** | Production | `http://ollama:11434/v1` | Docker Compose deployment (service name) |

## Setup

Choose the appropriate template for your environment:

### Development (Local)

```bash
cp models.dev.yaml models.yaml
```

This uses `localhost:11434` for Ollama, assuming you're running Ollama on your host machine or via `docker-compose.dev.yml`.

### Production (Docker Compose)

```bash
cp models.prod.yaml models.yaml
```

This uses `ollama:11434` which is the Docker service name in `docker-compose.yml`.

## Configuration Format

```yaml
models:
  - id: model-id              # Unique identifier
    name: Model Display Name  # Human-readable name
    model: model-name         # Model name for API calls
    base_url: https://...     # API endpoint
    api_key_env: ENV_VAR_NAME # Environment variable containing API key (null if not needed)
    organization: Org Name    # Model organization
    license: proprietary      # License type
```

## API Keys

**API keys are NEVER stored in this file.** Only the environment variable name is stored.

Set actual API keys in your environment file (`.env`, `.env.prod`):

```bash
# .env or .env.prod
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

## Adding Models

### External API Models (OpenAI, Anthropic, etc.)

```yaml
- id: gpt-4
  name: GPT-4
  model: gpt-4
  base_url: https://api.openai.com/v1
  api_key_env: OPENAI_API_KEY
  organization: OpenAI
  license: proprietary
```

### Self-Hosted Ollama Models

```yaml
- id: llama-3-1-8b
  name: Llama 3.1 8B
  model: llama3.1:8b
  base_url: http://localhost:11434/v1  # or http://ollama:11434/v1 in production
  api_key_env: null
  organization: Meta
  license: open-source
```

Don't forget to add the model to `OLLAMA_MODELS` in your environment file for automatic download:

```bash
OLLAMA_MODELS=llama3.1:8b,qwen2.5:7b,mistral:7b
```

## Security

- ✅ `models.dev.yaml` and `models.prod.yaml` are tracked in Git (templates only)
- ✅ `models.yaml` is in `.gitignore` (actual configuration, may be customized)
- ✅ API keys are stored in `.env` / `.env.prod` (also in `.gitignore`)
- ❌ Never commit API keys or sensitive credentials

## Troubleshooting

**Backend can't connect to Ollama:**
- Development: Check Ollama is running on `localhost:11434`
- Production: Ensure using `models.prod.yaml` with service name `ollama:11434`

**Model not found:**
- Check model name matches exactly (e.g., `llama3.1:8b` not `llama3.1`)
- For Ollama: Verify model is downloaded (`docker compose exec ollama ollama list`)

**API authentication failed:**
- Check API key environment variable is set
- Verify environment variable name matches `api_key_env` field
