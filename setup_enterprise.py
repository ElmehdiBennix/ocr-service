#!/usr/bin/env python3
"""
Enterprise OCR SaaS Setup Script

This script generates all necessary files for transforming the basic OCR service
into a production-ready SaaS platform with authentication, API versioning,
Swagger documentation, and a complete Docker Compose stack.

Run with: python3 setup_enterprise.py
"""

import os
import shutil
from pathlib import Path

# Define project structure
PROJECT_DIRS = [
    "app/routers/v1",
    "app/routers/v2",
    "app/core",
    "app/services",
    "app/middleware",
    "alembic/versions",
    "frontend/landing",
    "frontend/admin",
    "tests",
    "scripts",
    "docs",
    "nginx",
]

def create_directories():
    """Create all necessary directories."""
    print("Creating directory structure...")
    for dir_path in PROJECT_DIRS:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        # Create __init__.py for Python packages
        if dir_path.startswith("app/") or dir_path.startswith("tests/"):
            init_file = Path(dir_path) / "__init__.py"
            if not init_file.exists():
                init_file.write_text("# Auto-generated\\n")
    print("✓ Directory structure created")

def move_existing_files():
    """Move existing files to the new structure."""
    print("Reorganizing existing files...")
    
    # Move parsers.py to app/services/
    if os.path.exists("parsers.py"):
        shutil.move("parsers.py", "app/services/parsers.py")
        print("  ✓ Moved parsers.py to app/services/")
    
    # Archive old main.py
    if os.path.exists("main.py"):
        shutil.move("main.py", "main.py.old")
        print("  ✓ Archived old main.py")
    
    print("✓ Files reorganized")

def update_requirements():
    """Update requirements.txt with enterprise dependencies."""
    print("Updating requirements.txt...")
    
    requirements = """# Core Framework
fastapi==0.109.2
uvicorn[standard]==0.27.1
python-multipart==0.0.9

# Database
sqlalchemy[asyncio]==2.0.25
asyncpg==0.29.0
alembic==1.13.1
psycopg2-binary==2.9.9

# Authentication & Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
pyjwt==2.8.0
python-dotenv==1.0.1
pydantic-settings==2.1.0

# OCR Dependencies
python-magic==0.4.27
pytesseract==0.3.10
pdfplumber==0.11.0
python-docx==1.1.0
openpyxl==3.1.2
python-pptx==0.6.23
striprtf==0.0.26
beautifulsoup4==4.12.3
EbookLib==0.18
Pillow==10.2.0
lxml==5.1.0
odfpy==1.4.1
markdown-it-py==3.0.0
opencv-python==4.9.0.80

# Async & Background Tasks
celery==5.3.6
redis==5.0.1

# HTTP & Networking
httpx==0.26.0

# Monitoring & Logging
prometheus-client==0.19.0

# Testing
pytest==8.0.0
pytest-asyncio==0.23.4
pytest-cov==4.1.0
"""
    
    with open("requirements.txt", "w") as f:
        f.write(requirements)
    
    print("✓ Requirements updated")

def create_docker_compose():
    """Create Docker Compose configuration."""
    print("Creating Docker Compose stack...")
    
    compose_content = """version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:16-alpine
    container_name: ocr-postgres
    environment:
      POSTGRES_USER: ocr_user
      POSTGRES_PASSWORD: ocr_password
      POSTGRES_DB: ocr_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ocr_user -d ocr_db"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - ocr-network

  # Redis Cache & Queue
  redis:
    image: redis:7-alpine
    container_name: ocr-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - ocr-network

  # FastAPI Application
  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: ocr-api
    environment:
      DATABASE_URL: postgresql+asyncpg://ocr_user:ocr_password@postgres:5432/ocr_db
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: ${SECRET_KEY:-your-secret-key-change-in-production-minimum-32-characters-long}
      CELERY_BROKER_URL: redis://redis:6379/1
      CELERY_RESULT_BACKEND: redis://redis:6379/2
    volumes:
      - ./app:/app/app:ro
      - ./frontend:/app/frontend:ro
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - ocr-network
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  # Celery Worker
  celery-worker:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: ocr-celery
    environment:
      DATABASE_URL: postgresql+asyncpg://ocr_user:ocr_password@postgres:5432/ocr_db
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: ${SECRET_KEY:-your-secret-key-change-in-production-minimum-32-characters-long}
      CELERY_BROKER_URL: redis://redis:6379/1
      CELERY_RESULT_BACKEND: redis://redis:6379/2
    volumes:
      - ./app:/app/app:ro
    depends_on:
      - redis
      - postgres
    networks:
      - ocr-network
    command: celery -A app.celery_app worker --loglevel=info

  # Nginx Reverse Proxy (Production)
  nginx:
    image: nginx:alpine
    container_name: ocr-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./frontend:/usr/share/nginx/html:ro
    depends_on:
      - api
    networks:
      - ocr-network
    profiles:
      - production

volumes:
  postgres_data:
  redis_data:

networks:
  ocr-network:
    driver: bridge
"""
    
    with open("docker-compose.yml", "w") as f:
        f.write(compose_content)
    
    print("✓ Docker Compose configuration created")

def create_env_example():
    """Create .env.example file."""
    print("Creating .env.example...")
    
    env_content = """# Application Settings
APP_NAME=Enterprise OCR API
DEBUG=False

# Database
DATABASE_URL=postgresql+asyncpg://ocr_user:ocr_password@postgres:5432/ocr_db

# Redis
REDIS_URL=redis://redis:6379/0

# Security (CHANGE THESE IN PRODUCTION!)
SECRET_KEY=your-secret-key-change-in-production-minimum-32-characters-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# File Upload
MAX_FILE_SIZE=52428800  # 50MB in bytes

# Celery
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2

# Logging
LOG_LEVEL=INFO
"""
    
    with open(".env.example", "w") as f:
        f.write(env_content)
    
    print("✓ .env.example created")

def create_readme():
    """Create comprehensive README."""
    print("Creating README.md...")
    
    readme_content = """# Enterprise OCR Service

A production-grade, enterprise-ready OCR (Optical Character Recognition) SaaS platform built with FastAPI, PostgreSQL, Redis, and Celery.

## Features

### 🔐 Authentication & Authorization
- JWT-based authentication
- API key management
- Role-based access control (User, Business, Admin)
- Secure password hashing with bcrypt

### 📊 API Versioning
- **v1 API**: Stable production endpoints
- **v2 API**: Enhanced features with batch processing

### 📄 Document Support
Supports 15+ file formats:
- PDF, DOCX, XLSX, PPTX
- Images (PNG, JPG, TIFF, etc.)
- ODT, RTF, HTML, EPUB, Markdown, CSV

### 🚀 Enterprise Features
- Rate limiting and usage quotas
- Usage tracking and analytics
- Async batch processing with Celery
- Comprehensive API documentation (Swagger/ReDoc)
- Health checks and monitoring
- Admin dashboard

### 🐳 Production-Ready Infrastructure
- Docker Compose stack
- PostgreSQL database with connection pooling
- Redis for caching and queues
- Nginx reverse proxy
- Automated migrations with Alembic

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.9+ (for local development)
- Tesseract OCR (`apt-get install tesseract-ocr`)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ocr-service
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env and change SECRET_KEY and other sensitive values
   ```

3. **Start the services**
   ```bash
   docker-compose up -d
   ```

4. **Run database migrations**
   ```bash
   docker-compose exec api alembic upgrade head
   ```

5. **Create an admin user** (optional)
   ```bash
   docker-compose exec api python scripts/create_admin.py
   ```

6. **Access the API**
   - API: http://localhost:8000
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
   - Landing Page: http://localhost/
   - Admin Dashboard: http://localhost/admin/

## API Usage

### 1. Register a User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \\
  -H "Content-Type: application/json" \\
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \\
  -H "Content-Type: application/json" \\
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### 3. Create an API Key

```bash
curl -X POST "http://localhost:8000/api/v1/keys/create" \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "My API Key",
    "rate_limit": 100
  }'
```

### 4. Extract Text from Document

```bash
curl -X POST "http://localhost:8000/api/v1/ocr/extract" \\
  -H "X-API-Key: YOUR_API_KEY" \\
  -F "file=@document.pdf"
```

Response:
```json
{
  "filename": "document.pdf",
  "mime_type": "application/pdf",
  "content": "Extracted text from the document...",
  "file_size": 1024000,
  "processing_time": 2.5
}
```

## Project Structure

```
ocr-service/
├── app/
│   ├── core/              # Core utilities (security, config)
│   ├── middleware/        # Custom middleware (rate limiting, logging)
│   ├── models.py          # SQLAlchemy models
│   ├── schemas.py         # Pydantic schemas
│   ├── database.py        # Database connection
│   ├── routers/
│   │   ├── v1/            # API v1 endpoints
│   │   │   ├── auth.py    # Authentication
│   │   │   ├── users.py   # User management
│   │   │   ├── keys.py    # API key management
│   │   │   └── ocr.py     # OCR endpoints
│   │   └── v2/            # API v2 endpoints
│   ├── services/          # Business logic
│   │   ├── parsers.py     # Document parsers
│   │   └── usage.py       # Usage tracking
│   └── main.py            # FastAPI application
├── alembic/               # Database migrations
├── frontend/
│   ├── landing/           # Marketing website
│   └── admin/             # Admin dashboard
├── tests/                 # Test suite
├── nginx/                 # Nginx configuration
├── docker-compose.yml     # Docker Compose stack
├── Dockerfile             # Application container
└── requirements.txt       # Python dependencies
```

## Development

### Local Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Run database
docker-compose up -d postgres redis

# Run migrations
alembic upgrade head

# Start API server
uvicorn app.main:app --reload
```

### Running Tests

```bash
pytest tests/ -v --cov=app
```

## API Documentation

Full API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

See `docs/API.md` for detailed endpoint documentation.

## Security

### Production Checklist

- [ ] Change `SECRET_KEY` in `.env` (use `openssl rand -hex 32`)
- [ ] Update database credentials
- [ ] Configure CORS origins
- [ ] Set up HTTPS with SSL certificates
- [ ] Enable rate limiting
- [ ] Configure firewall rules
- [ ] Set up monitoring and alerts
- [ ] Regular database backups

## Deployment

### Using Docker Compose (Production)

```bash
# Build and start with production profile
docker-compose --profile production up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Environment Variables

See `.env.example` for all available configuration options.

## Monitoring

Access health checks:
- Overall health: `GET /health`
- Database health: `GET /health/db`
- Redis health: `GET /health/redis`
- Metrics (Prometheus): `GET /metrics`

## License

[Your License Here]

## Support

For issues and questions, please contact [your-email@example.com]

---

**Built with ❤️ using FastAPI, PostgreSQL, Redis, and Docker**
"""
    
    with open("README.md", "w") as f:
        f.write(readme_content)
    
    print("✓ README.md created")

def main():
    """Main setup function."""
    print("=" * 60)
    print("Enterprise OCR SaaS Setup")
    print("=" * 60)
    print()
    
    try:
        create_directories()
        move_existing_files()
        update_requirements()
        create_docker_compose()
        create_env_example()
        create_readme()
        
        print()
        print("=" * 60)
        print("✅ Setup Complete!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Review and customize .env.example, then copy to .env")
        print("2. Install Python dependencies: pip install -r requirements.txt")
        print("3. Run the comprehensive setup: python scripts/complete_setup.py")
        print("4. Start Docker services: docker-compose up -d")
        print("5. Run migrations: docker-compose exec api alembic upgrade head")
        print("6. Access Swagger UI: http://localhost:8000/docs")
        print()
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        raise

if __name__ == "__main__":
    main()
