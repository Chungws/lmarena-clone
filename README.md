# llmbattler - AI Language Model Battle Arena

> Compare and evaluate LLM responses through blind side-by-side testing

![Project Status](https://img.shields.io/badge/status-mvp%20complete-green)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![Next.js](https://img.shields.io/badge/next.js-15-black)
![FastAPI](https://img.shields.io/badge/fastapi-0.115+-green)

**llmbattler** is an open-source platform for comparing and evaluating Large Language Models through blind A/B testing. Users submit prompts to two randomly selected models, vote on the better response, and contribute to comprehensive ELO-based leaderboards.

Inspired by [LM Arena](https://lmarena.ai), built with modern web technologies.

---

## ✨ Features

- **Blind Testing**: Compare responses from two LLMs side-by-side without knowing which model is which
- **Multi-Turn Conversations**: Continue conversations after voting with follow-up messages
- **Session Management**: ChatGPT-like sidebar with conversation history
- **ELO Rankings**: Fair model comparison using chess-style ELO ratings with confidence intervals
- **Comprehensive Leaderboards**: Track model performance with real-time rankings
- **Flexible LLM Integration**: OpenAI-compatible API for easy model additions (Ollama, OpenAI, Anthropic, etc.)
- **Automated Aggregation**: Hourly worker updates leaderboards from user votes

---

## 🛠️ Tech Stack

### Backend
- **API Server**: FastAPI with async/await
- **Worker**: Python cron job (APScheduler) for vote aggregation and ELO calculation
- **Database**: PostgreSQL 16 (single database architecture)
- **ORM**: SQLModel + SQLAlchemy 2.0

### Frontend
- **Framework**: Next.js 15 with App Router
- **React**: v19 with React Server Components
- **UI Library**: shadcn/ui (Radix UI + Tailwind CSS v4)
- **State Management**: React Context API
- **Styling**: Tailwind CSS with dark mode support

### Infrastructure
- **Package Manager**: uv (Python workspace), npm (Frontend)
- **Containerization**: Docker + Docker Compose with profiles
- **Development**: Makefile for workflow automation
- **Migrations**: Alembic for database schema management

---

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose** (required for PostgreSQL + Ollama)
- **Node.js 18+** (for frontend development)
- **Python 3.11+** (for backend/worker development)
- **uv** (Python package manager): `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Make** (usually pre-installed on macOS/Linux)

### Local Development (Recommended)

```bash
# 1. Clone repository
git clone https://github.com/Chungws/lmarena-clone.git
cd lmarena-clone

# 2. Install dependencies
make setup

# 3. Configure environment
cp .env.example .env
# Edit .env if needed (defaults work for local development)

# 4. Start infrastructure (PostgreSQL + Ollama)
make dev-infra

# 5. Run services in separate terminals
# Terminal 1: Backend API
make dev-backend

# Terminal 2: Frontend
make dev-frontend

# Terminal 3: Worker (optional for local dev)
make dev-worker
```

**Endpoints:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Available Make Commands:**
```bash
make help         # Show all commands
make setup        # Install dependencies (first time only)
make dev          # Start infrastructure and show instructions
make dev-infra    # Start PostgreSQL + Ollama
make dev-backend  # Start Backend API
make dev-frontend # Start Frontend
make dev-worker   # Run Worker (vote aggregation)
make stop         # Stop Docker services
make clean        # Stop and remove all data (WARNING: deletes DB)
make test         # Run all tests
make lint         # Run all linters
```

---

## 🌐 Production Deployment

### Quick Production Deploy

**Server Requirements:**
- Ubuntu 20.04+ or similar Linux distribution
- 32GB RAM (for 6 lightweight Ollama models)
- 50GB disk space
- Public IP address

**Deploy in 5 minutes:**

```bash
# 1. Clone on server
ssh user@YOUR_SERVER_IP
git clone https://github.com/Chungws/lmarena-clone.git
cd lmarena-clone

# 2. Configure environment
cp .env.example .env
nano .env
# Required changes:
# - POSTGRES_PASSWORD=your_secure_password_here
# - POSTGRES_URI=postgresql+asyncpg://postgres:your_secure_password_here@postgres:5432/llmbattler
# - NEXT_PUBLIC_API_URL=http://YOUR_SERVER_IP:8000
# - CORS_ORIGINS=http://YOUR_SERVER_IP:3000

# 3. Deploy all services
docker compose --profile prod up -d

# 4. Open firewall
sudo ufw allow 3000/tcp
sudo ufw allow 8000/tcp

# 5. Watch logs (optional)
docker compose logs -f
```

**Access your deployment:**
- Frontend: `http://YOUR_SERVER_IP:3000`
- API: `http://YOUR_SERVER_IP:8000/docs`

**First startup takes 10-30 minutes** for Ollama to download models (gemma3:1b by default).

### Production Configuration

**Environment Variables (.env):**

Key settings to modify for production:

```bash
# Database (REQUIRED: Change password!)
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_URI=postgresql+asyncpg://postgres:your_secure_password_here@postgres:5432/llmbattler

# Frontend API URL
NEXT_PUBLIC_API_URL=http://YOUR_SERVER_IP:8000
# For domain: https://api.yourdomain.com

# CORS (must match frontend URL exactly)
CORS_ORIGINS=http://YOUR_SERVER_IP:3000
# For domain: https://yourdomain.com

# Ollama models (comma-separated)
OLLAMA_MODELS=gemma3:1b
# More models: tinyllama:1.1b,gemma2:2b,phi3:mini,qwen2.5:3b,mistral:7b,llama3.1:8b

# GPU (if available)
OLLAMA_GPU_ENABLED=0  # Set to 1 if you have NVIDIA GPU

# External API Keys (optional)
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
```

### Model Configuration

**Default (Development):** 10 variants of gemma3:1b (lightweight, for testing)

**Production Options:**

Edit `backend/config/models.yaml` to add models:

```yaml
models:
  # Ollama (self-hosted, free)
  - id: llama-3-1-8b
    name: Llama 3.1 8B
    model: llama3.1:8b
    base_url: http://ollama:11434/v1  # Production
    # base_url: http://localhost:11434/v1  # Development
    api_key_env: null
    organization: Meta
    license: open-source
    status: active

  # External APIs (requires API key)
  - id: gpt-4o-mini
    name: GPT-4o Mini
    model: gpt-4o-mini
    base_url: https://api.openai.com/v1
    api_key_env: OPENAI_API_KEY  # Set in .env
    organization: OpenAI
    license: proprietary
    status: active
```

**Recommended lightweight models for production** (32GB RAM total):
- tinyllama:1.1b (~2GB)
- gemma2:2b (~3GB)
- phi3:mini (~4GB)
- qwen2.5:3b (~4GB)
- mistral:7b (~6GB)
- llama3.1:8b (~7GB)

### Domain Setup with SSL (Optional)

For production with custom domain and HTTPS:

**1. Point DNS to your server:**
```
A Record: yourdomain.com → YOUR_SERVER_IP
A Record: api.yourdomain.com → YOUR_SERVER_IP
```

**2. Install Nginx + Certbot:**
```bash
sudo apt update
sudo apt install nginx certbot python3-certbot-nginx
```

**3. Configure Nginx:**
```bash
sudo nano /etc/nginx/sites-available/llmbattler
```

```nginx
# Backend API
server {
    listen 80;
    server_name api.yourdomain.com;
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Frontend
server {
    listen 80;
    server_name yourdomain.com;
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**4. Enable and get SSL:**
```bash
sudo ln -s /etc/nginx/sites-available/llmbattler /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com
```

**5. Update .env:**
```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
CORS_ORIGINS=https://yourdomain.com
```

**6. Restart services:**
```bash
docker compose restart backend frontend
```

### GPU Setup (Optional)

**Speeds up responses 3-10x!**

**Requirements:**
- NVIDIA GPU with 12GB+ VRAM
- Linux server

**Setup:**
```bash
# 1. Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
    sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker

# 2. Edit docker-compose.yml (uncomment GPU lines under ollama service)
nano docker-compose.yml

# 3. Update .env
nano .env
# OLLAMA_GPU_ENABLED=1

# 4. Restart
docker compose restart ollama backend
```

### Production Maintenance

**View logs:**
```bash
docker compose logs -f [service_name]
docker compose logs --tail=100 backend
```

**Update application:**
```bash
git pull origin develop
docker compose build
docker compose --profile prod up -d
```

**Backup database:**
```bash
docker compose exec postgres pg_dump -U postgres llmbattler > backup-$(date +%Y%m%d).sql
```

**Restore database:**
```bash
cat backup-20250123.sql | docker compose exec -T postgres psql -U postgres llmbattler
```

**Add/remove Ollama models:**
```bash
# Add model
docker compose exec ollama ollama pull mistral:7b
docker compose restart backend  # Reload model list

# Remove model
docker compose exec ollama ollama rm mistral:7b

# List models
docker compose exec ollama ollama list
```

**Monitor resources:**
```bash
docker stats
docker compose ps
```

### Troubleshooting

**Services not starting:**
```bash
docker compose ps
docker compose logs backend
docker compose logs postgres
```

**Frontend can't connect to backend:**
- Check CORS_ORIGINS matches frontend URL exactly (including protocol and port)
- Restart backend: `docker compose restart backend`

**Ollama models not downloading:**
```bash
# Check logs
docker compose logs -f ollama

# Manually download
docker compose exec ollama ollama pull gemma3:1b
```

**Out of memory:**
```bash
# Check memory
free -h
docker stats

# Use fewer/smaller models in .env
OLLAMA_MODELS=gemma3:1b,phi3:mini
```

---

## 📁 Project Structure

```
lmarena-clone2/
├── .env.example              # Environment variables template
├── Makefile                  # Development workflow automation
├── docker-compose.yml        # Docker services (dev + prod profiles)
│
├── backend/                  # FastAPI application (uv workspace member)
│   ├── src/
│   │   └── llmbattler_backend/
│   │       ├── main.py       # FastAPI app entry
│   │       ├── api/          # API routes
│   │       │   ├── battles.py
│   │       │   ├── sessions.py
│   │       │   ├── models.py
│   │       │   └── leaderboard.py
│   │       └── services/     # Business logic
│   ├── tests/                # pytest tests
│   ├── alembic/              # Database migrations
│   ├── config/
│   │   └── models.yaml       # LLM model configuration
│   ├── pyproject.toml
│   └── Dockerfile
│
├── worker/                   # Data aggregation worker (uv workspace member)
│   ├── src/
│   │   └── llmbattler_worker/
│   │       ├── main.py       # Worker entry (APScheduler)
│   │       └── aggregators/  # ELO calculation logic
│   ├── tests/
│   ├── pyproject.toml
│   └── Dockerfile
│
├── shared/                   # Shared code (uv workspace member)
│   ├── src/
│   │   └── llmbattler_shared/
│   │       ├── models.py     # SQLModel models (Session, Battle, Vote, etc.)
│   │       ├── schemas.py    # Pydantic schemas
│   │       └── config.py     # Settings (loads .env)
│   └── pyproject.toml
│
├── frontend/                 # Next.js application
│   ├── app/                  # App Router pages
│   │   ├── page.tsx          # Home page (redirects to /battle)
│   │   ├── battle/           # Battle mode page
│   │   └── leaderboard/      # Leaderboard page
│   ├── components/           # React components
│   │   ├── battle-card.tsx
│   │   ├── session-list.tsx
│   │   └── leaderboard-table.tsx
│   ├── lib/                  # Utilities & hooks
│   │   ├── apiClient.ts
│   │   └── hooks/
│   ├── package.json
│   └── Dockerfile
│
├── WORKSPACE/                # Documentation
│   ├── 00_PROJECT.md         # Project overview & policies
│   ├── 00_ROADMAP.md         # Development roadmap
│   ├── CONVENTIONS/          # Coding standards
│   ├── ARCHITECTURE/         # ADRs
│   └── FEATURES/             # Feature specifications
│
├── pyproject.toml            # uv workspace root
├── uv.lock                   # Unified Python lockfile
├── CLAUDE.md                 # AI assistant guidelines
└── README.md                 # This file
```

**Key Points:**
- **uv Workspace:** Backend, worker, and shared are Python workspace members
- **Flat Layout:** All members at root level (no nested `packages/` folder)
- **Single Lockfile:** `uv.lock` ensures consistent dependencies
- **Environment Priority:** Each service can override root `.env` with local `.env`

---

## 🏗️ Architecture Overview

```
┌─────────────────┐
│ Next.js Client  │ (Battle UI, Leaderboard, Session Sidebar)
└────────┬────────┘
         │
    ┌────▼─────────┐
    │ FastAPI API  │ (Sessions, Battles, Voting, Leaderboard)
    └────┬─────────┘
         │
         ├──► Ollama (http://localhost:11434/v1)
         │       └── Local LLM models (gemma3, llama, etc.)
         │
         ├──► External LLM APIs (optional)
         │       ├── OpenAI (GPT-4, etc.)
         │       └── Anthropic (Claude, etc.)
         │
         └──► PostgreSQL (sessions, battles, votes, model_stats)
                  │
             ┌────▼────────┐
             │   Worker    │ (Hourly ELO aggregation)
             └─────────────┘
```

**Key Design Decisions:**

1. **No Foreign Keys ([ADR-001](WORKSPACE/ARCHITECTURE/ADR_001-No_Foreign_Keys.md))**
   - Application-level relationships only
   - Simplifies testing (no dependency order in fixtures)
   - Easier development (no cascade deletion complexity)

2. **Session-Based Architecture**
   - sessions → battles → votes hierarchy
   - Multi-turn conversations with JSONB storage
   - Anonymous user IDs (localStorage UUID)

3. **PostgreSQL-Only**
   - Single database for MVP (10 QPS scale)
   - JSONB for conversation storage (OpenAI-compatible format)
   - Clear scalability path to 10,000+ QPS (sharding, read replicas)

4. **Blind Testing**
   - Model identities hidden until after voting
   - Fair comparison without brand bias

5. **ELO Rankings**
   - Chess-style ratings for model comparison
   - Bradley-Terry confidence intervals (95% CI)
   - Minimum 5 votes to appear on leaderboard

6. **Repository Pattern**
   - Clean abstraction for database operations
   - Easier to test and refactor
   - Prepares for future database changes

---

## 🧪 Development

### Pre-Commit Checks

Run before creating a PR:

```bash
# All checks
make lint
make test

# Or individually
cd backend && uvx ruff check && uvx ruff format --check && uvx isort --check --profile black .
cd backend && uv run pytest -s
cd worker && uvx ruff check && uvx ruff format --check && uvx isort --check --profile black .
cd worker && uv run pytest -s
cd frontend && npm run lint
```

### Git Workflow

This project uses Git Flow with `develop` as the main branch:

1. **Create feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes and commit:**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

3. **Push and create PR targeting `develop`:**
   ```bash
   git push -u origin feature/your-feature-name
   # Create PR on GitHub
   ```

4. **After merge, delete feature branch:**
   ```bash
   git checkout develop
   git pull
   git branch -d feature/your-feature-name
   ```

See [WORKSPACE/CONVENTIONS/GIT_FLOW.md](WORKSPACE/CONVENTIONS/GIT_FLOW.md) for details.

### Package Management

**Python (Backend/Worker/Shared):**
```bash
# Add dependency
cd backend
uv add fastapi

# Add dev dependency
uv add --dev pytest

# Sync entire workspace
cd .. && uv sync

# Run command
uv run pytest
```

**Frontend:**
```bash
cd frontend
npm install <package>
npm run dev
```

### Database Migrations

**Create migration:**
```bash
cd backend
uv run alembic revision --autogenerate -m "add new table"
```

**Apply migrations:**
```bash
cd backend
uv run alembic upgrade head
```

**Rollback:**
```bash
uv run alembic downgrade -1
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **[WORKSPACE/00_PROJECT.md](WORKSPACE/00_PROJECT.md)** | Comprehensive project overview, policies, Quick Start |
| **[WORKSPACE/00_ROADMAP.md](WORKSPACE/00_ROADMAP.md)** | Development roadmap and milestones |
| **[WORKSPACE/CONVENTIONS/](WORKSPACE/CONVENTIONS/)** | Coding standards, Git workflow, PR guidelines |
| **[WORKSPACE/ARCHITECTURE/](WORKSPACE/ARCHITECTURE/)** | Architecture Decision Records (ADRs) |
| **[WORKSPACE/FEATURES/](WORKSPACE/FEATURES/)** | Feature specifications and phase tracking |
| **[CLAUDE.md](CLAUDE.md)** | Guidelines for AI assistants working on this project |

**For Contributors:**
- **New to the project?** Start with [WORKSPACE/00_PROJECT.md](WORKSPACE/00_PROJECT.md)
- **Check current status:** [WORKSPACE/00_ROADMAP.md](WORKSPACE/00_ROADMAP.md)
- **Read coding standards:** [WORKSPACE/CONVENTIONS/](WORKSPACE/CONVENTIONS/)

---

## 🎯 Roadmap

**✅ Phase 0: Project Initialization (Completed - 2025-01-21)**
- Architecture design, tech stack selection
- WORKSPACE documentation
- Database design (PostgreSQL-only, no FK)
- Docker Compose configuration

**✅ Phase 1: Battle MVP (Completed - 2025-10-21)**
- Session & Battle Creation API
- Voting API with model reveal
- Model Management System
- Frontend Battle UI with follow-up messages

**✅ Phase 2: Leaderboard MVP (Completed - 2025-10-21)**
- Worker ELO Calculation with Bradley-Terry CI
- Leaderboard API with sorting/filtering
- Frontend Leaderboard UI with search

**✅ Phase 3: Session Management UI (Completed - 2025-10-23)**
- Backend Session List API
- ChatGPT-like sidebar with conversation history
- Anonymous user management (localStorage UUID)
- Vote button hover effects and auto-scroll
- Post-vote conversation flow

**🚀 Next Steps:**
- UI/UX Polish & Testing
- Production deployment optimization
- User authentication (replace anonymous UUID)
- Advanced features (multi-modal, model comparison, admin dashboard)

See [WORKSPACE/00_ROADMAP.md](WORKSPACE/00_ROADMAP.md) for full roadmap.

---

## 🤝 Contributing

Contributions are welcome! Please read our documentation before starting:

1. Read [WORKSPACE/00_PROJECT.md](WORKSPACE/00_PROJECT.md) for project overview and policies
2. Check [WORKSPACE/CONVENTIONS/](WORKSPACE/CONVENTIONS/) for coding standards
3. Follow the Git Flow workflow in [WORKSPACE/CONVENTIONS/GIT_FLOW.md](WORKSPACE/CONVENTIONS/GIT_FLOW.md)
4. Write PRs in English following [WORKSPACE/CONVENTIONS/PR_GUIDELINES.md](WORKSPACE/CONVENTIONS/PR_GUIDELINES.md)

**Key Project Policies:**
- ❌ **NO Foreign Keys** - Application-level relationships only ([ADR-001](WORKSPACE/ARCHITECTURE/ADR_001-No_Foreign_Keys.md))
- ✅ **Main Branch**: `develop`
- ✅ **PR Language**: English
- ✅ **Package Manager**: `uv` (Python), `npm` (Frontend)

---

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🔗 Resources

- **LM Arena (Inspiration)**: https://lmarena.ai
- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **Next.js Documentation**: https://nextjs.org/docs
- **shadcn/ui**: https://ui.shadcn.com
- **uv**: https://docs.astral.sh/uv
- **ELO Rating System**: https://en.wikipedia.org/wiki/Elo_rating_system

---

**Built with ❤️ by [Chungws](https://github.com/Chungws)**

**Last Updated:** 2025-10-25
