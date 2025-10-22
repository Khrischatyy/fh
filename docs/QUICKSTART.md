# Quick Start Guide - 5 Minutes to Running API

This guide will get your FastAPI backend running in under 5 minutes.

## Prerequisites

- Docker and Docker Compose installed
- Git

## Steps

### 1. Navigate to Project Directory

```bash
cd /Users/alexkhrishchatyi/www/funny-how/new_backend
```

### 2. Configure Environment (Optional for Testing)

The `.env` file is already created with default values. For a quick test, you can use it as-is. For production or full functionality, update:

```bash
nano .env
```

Update at minimum:
- `SECRET_KEY` (generate with: `openssl rand -hex 32`)
- For OAuth: `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`
- For payments: Stripe and Square keys

### 3. Build and Start Services

```bash
make dev-build
```

This single command will:
- Build Docker images for FastAPI, Celery
- Start PostgreSQL database
- Start Redis cache
- Start RabbitMQ message broker
- Start FastAPI with hot reload
- Start Celery worker

**Wait about 30-60 seconds for all services to be ready.**

### 4. Run Database Migrations

In a new terminal:

```bash
cd /Users/alexkhrishchatyi/www/funny-how/new_backend
make migrate message="initial migration"
make upgrade
```

### 5. Access the Application

Open your browser:

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **RabbitMQ Management**: http://localhost:15672 (username: `guest`, password: `guest`)

### 6. Test the API

#### Register a User

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "password_confirmation": "testpass123",
    "firstname": "Test",
    "lastname": "User"
  }'
```

#### Login

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

Save the `access_token` from the response.

#### Get User Info

```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Common Commands

```bash
# View logs
make logs

# Restart API
make restart

# Stop all services
make stop

# Clean up everything
make clean

# Run tests
make test

# Open database shell
make db-shell
```

## Troubleshooting

### Port Already in Use

If port 8000 is in use, update `docker-compose` or `.env`:
```bash
# In dev.yml, change ports:
ports:
  - "8001:8000"  # Changed from 8000:8000
```

### Database Connection Error

Wait for PostgreSQL to fully start (30 seconds), then retry migrations:
```bash
make upgrade
```

### View Container Logs

```bash
# API logs
docker-compose -f dev.yml logs -f api

# Database logs
docker-compose -f dev.yml logs -f db

# All logs
docker-compose -f dev.yml logs -f
```

### Reset Everything

```bash
make clean
rm -rf alembic/versions/*.py  # Keep __pycache__ ignored
make dev-build
make migrate message="initial migration"
make upgrade
```

## Next Steps

1. **Test Auth Endpoints**: Use the Swagger UI at `/docs` to test all auth endpoints
2. **Implement Remaining Modules**: Follow `IMPLEMENTATION_GUIDE.md`
3. **Add Your Business Logic**: Customize services for your needs
4. **Set Up Production**: Use `make prod` when ready

## Need Help?

- Check `README.md` for full documentation
- Check `IMPLEMENTATION_GUIDE.md` for development guidance
- View logs: `make logs`
- Check container status: `docker-compose -f dev.yml ps`

---

**Your FastAPI backend is now running! 🚀**

Visit http://localhost:8000/docs to start exploring the API.
