# Deployment Guide

Complete guide for deploying **llmbattler** using Docker Compose.

---

## 📋 Table of Contents

1. [Quick Start](#-quick-start) - Most common scenario (IP + Lightweight models)
2. [Deployment Scenarios](#-deployment-scenarios)
   - [Scenario A: IP-based with Lightweight Models](#scenario-a-ip-based-with-lightweight-models-recommended) (Recommended)
   - [Scenario B: Domain-based with SSL](#scenario-b-domain-based-with-ssl)
   - [Scenario C: Mixed (External APIs + Ollama)](#scenario-c-mixed-external-apis--ollama)
3. [GPU Setup](#-gpu-setup-optional)
4. [Troubleshooting](#-troubleshooting)
5. [Maintenance](#-maintenance)
6. [Production Hardening](#-production-hardening)

---

## 🚀 Quick Start

**Most common deployment:** IP-based with 6 lightweight Ollama models (no external APIs, no domain needed).

```bash
# 1. Clone on server
ssh user@YOUR_SERVER_IP
git clone https://github.com/Chungws/lmarena-clone.git
cd lmarena-clone

# 2. Configure environment
cp .env.prod.example .env.prod
nano .env.prod
# Edit: DOMAIN, NEXT_PUBLIC_API_URL, CORS_ORIGINS, POSTGRES_PASSWORD

# 3. Configure models (lightweight)
cp backend/config/models.prod-lightweight.yaml backend/config/models.yaml

# 4. Deploy
docker compose build
docker compose --env-file .env.prod up -d

# 5. Open firewall
sudo ufw allow 3000/tcp
sudo ufw allow 8000/tcp

# 6. Access
# Frontend: http://YOUR_SERVER_IP:3000
# API: http://YOUR_SERVER_IP:8000/docs
```

**Expected deployment time:** 20-40 minutes (including model downloads)

---

## 🎯 Deployment Scenarios

Choose the scenario that matches your needs.

### Comparison

| Scenario | Domain | SSL | Models | Complexity | Cost |
|----------|--------|-----|--------|------------|------|
| **A: IP + Lightweight** | ❌ | ❌ | 6 Ollama (1B-8B) | ⭐ Easy | Free |
| **B: Domain + SSL** | ✅ | ✅ | Mixed | ⭐⭐ Medium | Free-$$ |
| **C: External APIs** | ❌/✅ | ❌/✅ | OpenAI, Claude | ⭐⭐⭐ Hard | $$$ |

---

## Scenario A: IP-based with Lightweight Models (Recommended)

**Best for:** Testing, internal use, no budget for external APIs

**Requirements:**
- Server with public IP
- 32GB RAM
- 50GB disk
- No domain needed

### A1. Server Requirements

**Cloud Options:**
- AWS: `t3.2xlarge` (8 vCPU, 32GB RAM) - ~$240/month
- GCP: `n2-standard-8` (8 vCPU, 32GB RAM) - ~$280/month
- Hetzner: Dedicated server - ~$50-100/month

### A2. Model Selection

6 lightweight Ollama models (no external API costs):

| Model | Size | RAM | Organization | Features |
|-------|------|-----|--------------|----------|
| TinyLlama 1.1B | 1.1B | ~2GB | TinyLlama | Fastest |
| Gemma 2 2B | 2B | ~3GB | Google | Efficient |
| Phi-3 Mini | 3B | ~4GB | Microsoft | Best ratio |
| Qwen 2.5 3B | 3B | ~4GB | Alibaba | Multilingual |
| Mistral 7B | 7B | ~6GB | Mistral AI | Popular |
| Llama 3.1 8B | 8B | ~7GB | Meta | Latest |

**Total:** ~26GB RAM, ~15GB download

### A3. Configuration

**Step 1: Edit `.env.prod`**

```bash
cp .env.prod.example .env.prod
nano .env.prod
```

**Required changes (replace `203.0.113.50` with your actual IP):**

```bash
# Server IP configuration
DOMAIN=203.0.113.50
NEXT_PUBLIC_API_URL=http://203.0.113.50:8000
FRONTEND_URL=http://203.0.113.50:3000
CORS_ORIGINS=http://203.0.113.50:3000

# Database password (CHANGE THIS!)
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_URI=postgresql+asyncpg://postgres:your_secure_password_here@postgres:5432/llmbattler

# Models to download (already configured correctly)
OLLAMA_MODELS=tinyllama:1.1b,gemma2:2b,phi3:mini,qwen2.5:3b,mistral:7b,llama3.1:8b

# GPU (set to 0 if no GPU)
OLLAMA_GPU_ENABLED=0

# API keys - NOT NEEDED for lightweight deployment
# Leave commented out
```

**Step 2: Configure models**

```bash
cp backend/config/models.prod-lightweight.yaml backend/config/models.yaml
```

### A4. Deploy

```bash
# Build images
docker compose build

# Start services
docker compose --env-file .env.prod up -d

# Watch model downloads (10-30 minutes)
docker compose logs -f ollama
```

### A5. Open Firewall

```bash
# Ubuntu/Debian
sudo ufw allow 3000/tcp
sudo ufw allow 8000/tcp
sudo ufw status

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=3000/tcp
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

**Cloud Providers:** Configure Security Groups to allow ports 3000, 8000.

### A6. Verify

```bash
# Check services
docker compose ps

# Should show all healthy:
# llmbattler-postgres   Up (healthy)
# llmbattler-backend    Up (healthy)
# llmbattler-worker     Up
# llmbattler-ollama     Up (healthy)
# llmbattler-frontend   Up (healthy)

# Check models downloaded
docker compose exec ollama ollama list

# Test API
curl http://localhost:8000/health
```

### A7. Access

Open browser:
- **Frontend:** `http://203.0.113.50:3000`
- **API Docs:** `http://203.0.113.50:8000/docs`

**⚠️ Security Warning:** This setup uses HTTP (no encryption). Suitable for testing/internal networks only. For public deployment, see [Scenario B](#scenario-b-domain-based-with-ssl).

---

## Scenario B: Domain-based with SSL

**Best for:** Production deployment, public access, professional setup

**Requirements:**
- Domain name (e.g., `yourdomain.com`)
- Server with public IP
- Same hardware as Scenario A

### B1. Domain Setup

Point your domain to server IP:

```
A Record:     yourdomain.com → YOUR_SERVER_IP
A Record:     api.yourdomain.com → YOUR_SERVER_IP
```

Wait for DNS propagation (5-60 minutes).

### B2. Configuration

**Edit `.env.prod`:**

```bash
# Domain configuration
DOMAIN=yourdomain.com
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
FRONTEND_URL=https://yourdomain.com
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Database password
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_URI=postgresql+asyncpg://postgres:your_secure_password_here@postgres:5432/llmbattler

# API Keys (optional)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Models (can use mixed: external + Ollama)
OLLAMA_MODELS=llama3.1:8b,mistral:7b
```

**Choose models:**

```bash
# Option 1: Lightweight only
cp backend/config/models.prod-lightweight.yaml backend/config/models.yaml

# Option 2: Mixed (external APIs + Ollama)
cp backend/config/models.prod.yaml backend/config/models.yaml
```

### B3. Setup Nginx + SSL

**Install Nginx:**

```bash
sudo apt update
sudo apt install nginx certbot python3-certbot-nginx
```

**Configure Nginx:**

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
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Frontend
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Enable site:**

```bash
sudo ln -s /etc/nginx/sites-available/llmbattler /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**Get SSL certificates:**

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com -d api.yourdomain.com
```

Certbot will automatically configure HTTPS and redirects.

### B4. Deploy

```bash
docker compose build
docker compose --env-file .env.prod up -d
```

### B5. Access

- **Frontend:** `https://yourdomain.com`
- **API:** `https://api.yourdomain.com/docs`

---

## Scenario C: Mixed (External APIs + Ollama)

**Best for:** Production with budget, best model variety

**Configuration:**

```bash
# .env.prod
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
OLLAMA_MODELS=llama3.1:8b,mistral:7b

# models.yaml - include both external and Ollama
cp backend/config/models.prod.yaml backend/config/models.yaml
```

**Cost estimate:**
- OpenAI GPT-4: ~$0.03 per 1K tokens
- Anthropic Claude: ~$0.015 per 1K tokens
- Ollama: Free (hosting cost only)

**Typical usage:** 1000 battles/day = ~$5-20/day depending on models.

---

## 🎮 GPU Setup (Optional)

**Speeds up responses 3-10x!**

### Prerequisites

- NVIDIA GPU with 12GB+ VRAM
- Linux server

### Installation

**1. Install NVIDIA Container Toolkit:**

```bash
# Ubuntu/Debian
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
    sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

**2. Enable GPU in docker-compose.yml:**

```bash
nano docker-compose.yml
```

Uncomment these lines under `ollama` service:

```yaml
ollama:
  runtime: nvidia  # Uncomment
  environment:
    - NVIDIA_VISIBLE_DEVICES=all  # Uncomment
```

**3. Update .env.prod:**

```bash
OLLAMA_GPU_ENABLED=1
OLLAMA_NUM_GPU=1
```

**4. Restart:**

```bash
docker compose restart ollama backend
```

**5. Verify:**

```bash
docker compose exec ollama nvidia-smi
```

---

## 🐛 Troubleshooting

### Frontend can't connect to backend

**Symptoms:** "Failed to fetch" or CORS errors

**Solution:** Check CORS_ORIGINS matches frontend URL exactly (including port):

```bash
# IP-based
CORS_ORIGINS=http://203.0.113.50:3000

# Domain-based
CORS_ORIGINS=https://yourdomain.com
```

Restart backend:
```bash
docker compose restart backend
```

### Services not starting

**Check logs:**
```bash
docker compose logs backend
docker compose logs ollama
docker compose logs postgres
```

**Common issues:**

1. **Database connection failed**
   ```bash
   # Check PostgreSQL is healthy
   docker compose ps postgres
   docker compose exec postgres pg_isready -U postgres
   ```

2. **Port already in use**
   ```bash
   # Find process using port
   sudo lsof -i :3000
   sudo lsof -i :8000

   # Kill if needed
   sudo kill -9 <PID>
   ```

3. **Out of memory**
   ```bash
   # Check memory usage
   free -h
   docker stats

   # Reduce models
   OLLAMA_MODELS=tinyllama:1.1b,gemma2:2b,phi3:mini
   ```

### Ollama models not downloading

**Check progress:**
```bash
docker compose logs -f ollama
```

**Manually download:**
```bash
docker compose exec ollama ollama pull tinyllama:1.1b
docker compose exec ollama ollama list
```

**Slow downloads:** Download one at a time:
```bash
OLLAMA_MODELS=tinyllama:1.1b  # Start with one
# After it downloads, add more manually
```

### Backend health check failing

**Check migrations:**
```bash
docker compose exec backend uv run alembic current
docker compose exec backend uv run alembic upgrade head
```

**Check environment variables:**
```bash
docker compose exec backend env | grep POSTGRES_URI
```

### Very slow responses

**CPU-only is slow. Solutions:**

1. **Add GPU** (see GPU Setup section)
2. **Use smaller models**
   ```bash
   OLLAMA_MODELS=tinyllama:1.1b,gemma2:2b,phi3:mini
   ```
3. **Use quantized versions**
   ```bash
   OLLAMA_MODELS=llama3.1:8b-q4_0,mistral:7b-q4_0
   ```

---

## 🔧 Maintenance

### Update Application

```bash
# Pull latest code
git pull origin main

# Rebuild
docker compose build

# Restart with new images
docker compose --env-file .env.prod up -d

# Check logs
docker compose logs -f
```

### Update Models

**Add new models:**
```bash
# Edit .env.prod
OLLAMA_MODELS=tinyllama:1.1b,gemma2:2b,phi3:mini,deepseek-coder:6.7b

# Restart Ollama
docker compose restart ollama

# Watch download
docker compose logs -f ollama

# Restart backend to recognize new models
docker compose restart backend
```

**Remove models:**
```bash
docker compose exec ollama ollama rm mistral:7b
```

### Backup

**Database:**
```bash
# Backup
docker compose exec postgres pg_dump -U postgres llmbattler > backup-$(date +%Y%m%d).sql

# Restore
cat backup-20250123.sql | docker compose exec -T postgres psql -U postgres llmbattler
```

**Ollama models (optional):**
```bash
# Models can be re-downloaded, but to backup:
docker compose exec ollama tar czf /tmp/ollama-models.tar.gz /root/.ollama
docker compose cp ollama:/tmp/ollama-models.tar.gz ./ollama-models.tar.gz
```

### Monitor Resources

```bash
# Real-time stats
docker stats

# Disk usage
docker system df
df -h

# Check logs size
du -sh /var/lib/docker/containers/*/*-json.log
```

### Logs Management

```bash
# View logs
docker compose logs -f [service_name]

# Last 100 lines
docker compose logs --tail=100 backend

# Follow specific service
docker compose logs -f ollama

# Save logs to file
docker compose logs > logs-$(date +%Y%m%d).txt
```

---

## 🔒 Production Hardening

### Security Checklist

- [ ] Change default PostgreSQL password
- [ ] Set strong `POSTGRES_PASSWORD`
- [ ] Remove database port exposure (comment out `ports: 5432:5432` in docker-compose.yml)
- [ ] Use HTTPS with SSL certificates (Let's Encrypt)
- [ ] Keep API keys secure (never commit `.env.prod`)
- [ ] Setup firewall rules (UFW/iptables)
- [ ] Regularly update Docker images
- [ ] Monitor logs for suspicious activity
- [ ] Implement rate limiting (future)
- [ ] Add authentication system (future)

### Close Database Port

Edit `docker-compose.yml`:

```yaml
postgres:
  # ports:
  #   - "5432:5432"  # Comment out - internal access only
```

### Rate Limiting

Add to backend (future enhancement):

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/battles/create")
@limiter.limit("10/minute")
async def create_battle(...):
    ...
```

### Monitoring (Optional)

Add Prometheus + Grafana:

```yaml
# docker-compose.yml
prometheus:
  image: prom/prometheus
  ports:
    - "9090:9090"
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml

grafana:
  image: grafana/grafana
  ports:
    - "3001:3000"
  depends_on:
    - prometheus
```

---

## 📊 Performance Expectations

### Response Times

**CPU-only (no GPU):**

| Model | First Token | Full Response (100 tokens) |
|-------|-------------|----------------------------|
| TinyLlama 1.1B | ~0.5s | ~5s |
| Gemma 2 2B | ~0.8s | ~8s |
| Phi-3 Mini 3B | ~1.0s | ~10s |
| Qwen 2.5 3B | ~1.0s | ~10s |
| Mistral 7B | ~2.0s | ~20s |
| Llama 3.1 8B | ~2.5s | ~25s |

**With GPU (NVIDIA 12GB+):** 3-10x faster

### Resource Usage

```
RAM Usage:
- PostgreSQL: ~200MB
- Backend: ~500MB
- Frontend: ~200MB
- Worker: ~200MB
- Ollama: 2-7GB per model loaded

Disk Space:
- Images: ~8GB
- Ollama models: ~15GB (6 models)
- Database: ~50-500MB (depends on usage)
```

### Scaling

**Current Setup:** Handles ~10 QPS (queries per second)

**For higher load:**
- Scale backend horizontally (multiple replicas)
- Add Redis for caching
- Use load balancer (Nginx)
- Separate database server
- Multiple Ollama workers

---

## 💰 Cost Estimation

### Infrastructure

**Cloud (24/7):**

| Provider | Instance | vCPU | RAM | Cost/month |
|----------|----------|------|-----|------------|
| AWS EC2 | t3.2xlarge | 8 | 32GB | ~$240 |
| AWS EC2 | g4dn.xlarge (GPU) | 4 | 16GB | ~$380 |
| GCP | n2-standard-8 | 8 | 32GB | ~$280 |
| Azure | Standard_D8s_v3 | 8 | 32GB | ~$275 |
| Hetzner | Dedicated | 8 | 64GB | ~$50-100 |

**Budget Options:**
- Hetzner Cloud: ~$40-60/month
- Digital Ocean: ~$160/month (32GB droplet)

### External API Costs (if used)

**Assumptions:** 1000 battles/day, avg 200 tokens per response

| Service | Model | Cost/1K tokens | Daily Cost | Monthly Cost |
|---------|-------|----------------|------------|--------------|
| OpenAI | GPT-4o-mini | $0.15/$0.60 (in/out) | ~$10 | ~$300 |
| Anthropic | Claude 3.5 Sonnet | $3/$15 (in/out) | ~$50 | ~$1500 |
| Ollama | Self-hosted | Free | $0 | $0 |

**Recommendation:** Start with Ollama-only (free), add external APIs as needed.

---

## 🆘 Getting Help

**Documentation:**
- Project README: [README.md](README.md)
- Backend config: [backend/config/README.md](backend/config/README.md)
- Model configuration guide in `backend/config/`

**GitHub:**
- Report issues: https://github.com/Chungws/lmarena-clone/issues
- Check existing issues before creating new ones

**Logs to include when reporting issues:**
```bash
docker compose ps
docker compose logs backend > backend.log
docker compose logs ollama > ollama.log
# Attach logs to issue
```

---

## 🎯 Quick Reference

### Common Commands

```bash
# Start services
docker compose --env-file .env.prod up -d

# Stop services
docker compose down

# View logs
docker compose logs -f [service]

# Restart service
docker compose restart [service]

# Check status
docker compose ps

# Shell into container
docker compose exec backend bash
docker compose exec ollama sh

# Database access
docker compose exec postgres psql -U postgres llmbattler

# Ollama commands
docker compose exec ollama ollama list
docker compose exec ollama ollama pull model:tag
docker compose exec ollama ollama rm model:tag

# Rebuild and restart
docker compose build
docker compose --env-file .env.prod up -d

# Clean up (CAREFUL - removes data!)
docker compose down -v
docker system prune -a
```

### File Locations

```
Configuration:
- Environment: .env.prod
- Models: backend/config/models.yaml
- Docker: docker-compose.yml

Data (Docker volumes):
- PostgreSQL: llmbattler_postgres_data
- Ollama models: llmbattler_ollama_data

Logs:
- docker compose logs [service]
```

---

**Last Updated:** 2025-01-23
