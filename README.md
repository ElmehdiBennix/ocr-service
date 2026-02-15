# Enterprise OCR Service

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
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
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
curl -X POST "http://localhost:8000/api/v1/keys/create" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My API Key",
    "rate_limit": 100
  }'
```

### 4. Extract Text from Document

```bash
curl -X POST "http://localhost:8000/api/v1/ocr/extract" \
  -H "X-API-Key: YOUR_API_KEY" \
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
source venv/bin/activate  # On Windows: venv\Scripts\activate

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
