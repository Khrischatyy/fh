# Deployment Guide

Quick reference for deploying code changes to production.

## 🚀 Quick Commands (Most Common)

### Frontend Changes
```bash
# Fast rebuild with caching (30-60 seconds) ⚡
make prod-update-frontend

# Full rebuild without cache (5+ minutes) 🐌 - Only if dependencies changed!
make prod-rebuild-frontend
```

### Backend (FastAPI) Changes
```bash
# Restart API (picks up code changes automatically with volume mount)
docker-compose -f prod.yml restart api

# Full rebuild (if requirements.txt changed)
docker-compose -f prod.yml up -d --build api
```

### Chat Service Changes
```bash
# Restart chat service
docker-compose -f prod.yml restart chat

# Full rebuild
docker-compose -f prod.yml up -d --build chat
```

---

## 📦 Understanding Docker Layer Caching

### How It Works

Docker builds images in layers and caches unchanged layers:

```dockerfile
FROM node:20.11-alpine        # Layer 1: Base image (cached)
COPY package.json ./          # Layer 2: Dependencies manifest (cached if unchanged)
RUN npm install               # Layer 3: Install deps (cached if package.json unchanged) ⬅️ SAVES TIME!
COPY . .                      # Layer 4: Application code (always new)
RUN npm run build             # Layer 5: Build app (runs if code changed)
```

**Key Point:** If `package.json` hasn't changed, Docker skips the slow `npm install` step!

### Speed Comparison

| Command | Caching | Time | When to Use |
|---------|---------|------|-------------|
| `make prod-update-frontend` | ✅ Uses cache | ~30-60s | **Default** - Changed code only |
| `make prod-rebuild-frontend` | ❌ `--no-cache` flag | ~5-10min | Changed `package.json` dependencies |

---

## 🎯 When to Use Each Command

### Frontend Deployment

#### ⚡ **Fast Update** (99% of the time)
Use when you changed:
- Vue components (`.vue` files)
- TypeScript/JavaScript code
- CSS/SCSS styles
- Composables, pages, layouts
- Any code in `src/`

```bash
make prod-update-frontend
```

**Why it's fast:** Reuses cached `npm install` step

#### 🐌 **Full Rebuild** (rarely needed)
Use when you changed:
- `package.json` (added/removed npm packages)
- `package-lock.json` (dependency updates)
- `Dockerfile` itself

```bash
make prod-rebuild-frontend
```

**Why it's slow:** Reinstalls all npm packages from scratch

---

## 🔧 Backend & Services

### FastAPI Backend

The backend uses **volume mounts** in production, so code changes are picked up automatically with a restart:

```bash
# Just restart (picks up code changes)
docker-compose -f prod.yml restart api

# Rebuild (if requirements.txt or Dockerfile changed)
docker-compose -f prod.yml up -d --build api
```

### Chat Service (Socket.io)

```bash
# Restart only
docker-compose -f prod.yml restart chat

# Rebuild and restart
docker-compose -f prod.yml up -d --build chat
```

---

## 📊 Complete Workflow Examples

### Example 1: Fixed a bug in a Vue component

```bash
# Edit the file
vim frontend/client/src/pages/chats/[id].vue

# Deploy (fast)
make prod-update-frontend

# Check logs
docker-compose -f prod.yml logs -f frontend
```

**Time:** ~45 seconds

---

### Example 2: Added a new npm package

```bash
# Added package to package.json
vim frontend/client/package.json

# Deploy (slow, but necessary)
make prod-rebuild-frontend

# Check logs
docker-compose -f prod.yml logs -f frontend
```

**Time:** ~6 minutes (unavoidable - needs to install new package)

---

### Example 3: Fixed backend API endpoint

```bash
# Edit the file
vim backend/src/bookings/router.py

# Just restart (code mounted via volume)
docker-compose -f prod.yml restart api

# Check logs
docker-compose -f prod.yml logs -f api
```

**Time:** ~5 seconds

---

### Example 4: Updated Python dependencies

```bash
# Modified requirements
vim backend/requirements.txt

# Rebuild API
docker-compose -f prod.yml up -d --build api

# Check logs
docker-compose -f prod.yml logs -f api
```

**Time:** ~2-3 minutes

---

## 🛠️ Troubleshooting

### Frontend not picking up changes?

```bash
# Check if container is running
docker ps | grep frontend

# Force rebuild with cache
make prod-update-frontend

# Nuclear option: full rebuild
make prod-rebuild-frontend
```

### "ContainerConfig" Error

This happens when Docker's cache is corrupted:

```bash
# Remove old container
docker rm -f funny-how-frontend-prod

# Rebuild
make prod-update-frontend
```

### Site returns 502 Bad Gateway

Frontend container is not running:

```bash
# Check status
docker ps -a | grep frontend

# Check logs
docker logs funny-how-frontend-prod

# Restart if running
docker-compose -f prod.yml restart frontend

# Start if stopped
docker-compose -f prod.yml up -d frontend
```

### Build is stuck

```bash
# Check if build is running
ps aux | grep "docker-compose"

# Kill stuck build
pkill -f "docker-compose.*build"

# Clean up and retry
docker-compose -f prod.yml down
make prod-update-frontend
```

---

## 🎓 Pro Tips

### 1. Check what changed before deploying
```bash
git status
git diff
```

### 2. Tail logs in real-time
```bash
docker-compose -f prod.yml logs -f frontend
docker-compose -f prod.yml logs -f api
docker-compose -f prod.yml logs -f chat
```

### 3. Quick health check
```bash
# Check all services
docker ps --format "table {{.Names}}\t{{.Status}}"

# Test site
curl -I https://funny-how.com
```

### 4. Restart all services
```bash
docker-compose -f prod.yml restart
```

### 5. View resource usage
```bash
docker stats
```

---

## 📝 Summary Cheat Sheet

| What Changed | Command | Time |
|--------------|---------|------|
| Frontend code (Vue/JS/CSS) | `make prod-update-frontend` | 30-60s |
| Frontend dependencies (`package.json`) | `make prod-rebuild-frontend` | 5-10min |
| Backend code (Python files) | `docker-compose -f prod.yml restart api` | 5s |
| Backend dependencies (`requirements.txt`) | `docker-compose -f prod.yml up -d --build api` | 2-3min |
| Chat service code | `docker-compose -f prod.yml restart chat` | 5s |
| Database migrations | `make migrate-prod` | 10s |

---

## 🔍 Useful Commands

```bash
# View all running containers
docker ps

# View all containers (including stopped)
docker ps -a

# Check container logs
docker logs <container-name>

# Execute command in container
docker exec -it <container-name> bash

# View container resource usage
docker stats

# Clean up unused images/containers
docker system prune -a

# Restart specific service
docker-compose -f prod.yml restart <service-name>

# Stop all services
docker-compose -f prod.yml stop

# Start all services
docker-compose -f prod.yml up -d

# View service status
docker-compose -f prod.yml ps
```

---

## ⚠️ Important Notes

1. **Never use `--no-cache` unless absolutely necessary** - It wastes 5+ minutes reinstalling unchanged dependencies

2. **Check logs after deployment** - Make sure the service started successfully:
   ```bash
   docker logs funny-how-frontend-prod --tail 50
   ```

3. **Frontend builds take time** - Even with caching, Nuxt build takes 30-60 seconds. This is normal.

4. **Backend is faster** - Code changes don't require rebuild, just restart (5 seconds)

5. **Database changes need migrations** - Don't forget to run migrations after model changes:
   ```bash
   make migrate-prod
   ```

---

## 🆘 Need Help?

- Check CLAUDE.md for project architecture details
- Check logs: `docker-compose -f prod.yml logs -f <service>`
- Verify all services running: `docker ps`
- Check Makefile for all available commands: `cat Makefile | grep "^[a-z]"`
