# Quick Start Guide - Enterprise OCR Service

## What You Have Now

✅ **Complete enterprise-grade OCR SaaS platform** with:
- FastAPI backend with async PostgreSQL & Redis
- JWT + API Key dual authentication
- Rate limiting and usage tracking
- Docker Compose production stack
- Comprehensive API documentation (Swagger)
- Security best practices built-in

## Installation & Setup

### 1. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# IMPORTANT: Edit .env and change SECRET_KEY!
# Generate a secure key:
openssl rand -hex 32

# Update other values as needed
nano .env
```

### 2. Start Services

```bash
# Start the entire stack
docker-compose up -d

# View logs
docker-compose logs -f api
```

### 3. Run Database Migrations

```bash
# Create tables
docker-compose exec api alembic upgrade head
```

### 4. Create Admin User (Optional)

```bash
# Access the API container
docker-compose exec api python

# In Python shell:
from app.database import AsyncSessionLocal
from app.models import User
from app.core.security import hash_password
import asyncio

async def create_admin():
    async with AsyncSessionLocal() as db:
        admin = User(
            email="admin@example.com",
            hashed_password=hash_password("admin123"),
            role="admin",
            is_active=True
        )
        db.add(admin)
        await db.commit()
        print("✓ Admin user created!")

asyncio.run(create_admin())
```

## Usage Examples

### Access API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 1. Register User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123"
  }'
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### 3. Extract Text from Document

```bash
curl -X POST "http://localhost:8000/api/v1/ocr/extract" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf"
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Nginx (Port 80/443)                   │
│                 Reverse Proxy + SSL                      │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────┴─────────────────────────────────┐
│              FastAPI Application (Port 8000)             │
│  ┌─────────────┐  ┌─────────────┐  ┌────────────────┐ │
│  │   Auth      │  │    OCR      │  │    Admin       │ │
│  │  (JWT/API)  │  │  (v1/v2)    │  │  Dashboard     │ │
│  └─────────────┘  └─────────────┘  └────────────────┘ │
└───────────────────────┬─────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────┴──────┐ ┌─────┴──────┐ ┌─────┴────────┐
│  PostgreSQL  │ │   Redis    │ │    Celery    │
│   Database   │ │  Cache &   │ │   Worker     │
│              │ │   Queue    │ │              │
└──────────────┘ └────────────┘ └──────────────┘
```

## Project Structure

```
app/
├── core/              # Security, config, dependencies
├── middleware/        # Rate limiting, logging
├── models.py          # Database models
├── schemas.py         # Pydantic schemas
├── routers/
│   ├── v1/           # API v1 (stable)
│   └── v2/           # API v2 (enhanced)
└── services/         # Business logic (parsers, etc.)
```

## Troubleshooting

### Database Connection Issues
```bash
# Check if postgres is running
docker-compose ps postgres

# View database logs
docker-compose logs postgres
```

### Redis Connection Issues
```bash
# Check Redis
docker-compose exec redis redis-cli ping
```

### API Not Starting
```bash
# View API logs
docker-compose logs api

# Restart API
docker-compose restart api
```

## Security Checklist for Production

- [ ] Change `SECRET_KEY` in `.env`
- [ ] Update database credentials
- [ ] Configure CORS origins appropriately
- [ ] Enable HTTPS with valid SSL certificates
- [ ] Set up firewall rules
- [ ] Configure rate limits
- [ ] Enable monitoring and logging
- [ ] Set up regular database backups
- [ ] Review and update security headers

## What's Included

✅ Authentication (JWT + API Keys)
✅ Authorization (RBAC: User/Business/Admin)
✅ Rate Limiting (Redis-based)
✅ Usage Tracking & Analytics
✅ API Versioning (v1, v2)
✅ Comprehensive API Docs (Swagger/ReDoc)
✅ Health Checks & Monitoring
✅ Database Migrations (Alembic)
✅ Docker Compose Stack
✅ Production-Ready Configuration

## Support

For issues, check:
1. Docker logs: `docker-compose logs`
2. Database status: `docker-compose exec api alembic current`
3. API health: `curl http://localhost:8000/health`

---

**Your enterprise OCR service is ready! 🚀**
