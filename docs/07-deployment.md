# Deployment Guide — Elody-Farm Loyalty

## 1. Prerequisites

- Docker 24.0+
- Docker Compose 2.20+
- 4GB RAM minimum
- 20GB disk space

---

## 2. Environment Variables

Create `.env` file:

```bash
# Django
DEBUG=False
DJANGO_SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=api.elody-farm.md,localhost

# Database
DATABASE_URL=postgres://postgres:postgres@postgres:5432/elody_farm

# Redis
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# JWT
JWT_SECRET_KEY=your-jwt-secret-key

# SMS Provider
SMS_PROVIDER=infobip
SMS_API_KEY=your-sms-api-key
SMS_API_URL=https://api.infobip.com

# Storage (MinIO)
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=elody-farm
MINIO_PUBLIC_URL=http://localhost:9000

# Caddy
CADDY_HOST=localhost
CADDY_PORT=80

# Email (dev)
EMAIL_HOST=mailpit
EMAIL_PORT=1025
```

---

## 3. Running with Docker Compose

### 3.1 Development

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f web

# Stop services
docker-compose down
```

### 3.2 Production

```bash
# Build and start
docker-compose -f docker-compose.yml up -d --build

# Scale web workers
docker-compose up -d --scale web=3
```

---

## 4. Service URLs

| Service | URL | Description |
|---------|-----|-------------|
| API | http://localhost/api/v1/ | Django Ninja API |
| Admin | http://localhost/admin/ | Django Admin |
| Swagger | http://localhost/api/v1/docs | API Documentation |
| Mailpit | http://localhost:8025 | Email testing |
| MinIO Console | http://localhost:9001 | File storage |

---

## 5. Database Setup

### 5.1 Initial Setup

```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Load initial data
docker-compose exec web python manage.py loaddata initial_data
```

### 5.2 Backup

```bash
# Backup database
docker-compose exec postgres pg_dump -U postgres elody_farm > backup.sql

# Restore database
docker-compose exec -T postgres psql -U postgres elody_farm < backup.sql
```

---

## 6. Celery Tasks

### 6.1 Available Tasks

```bash
# Run specific task
docker-compose exec celery celery -A config call tasks.authn.cleanup_expired_otp

# View scheduled tasks
docker-compose exec celery-beat celery -A config beat --schedule
```

### 6.2 Monitoring

Flower provides Celery monitoring at http://localhost:5555

---

## 7. Troubleshooting

### 7.1 Common Issues

**Database connection error:**
```bash
# Check database is running
docker-compose ps postgres

# Check connection
docker-compose exec web python -c "import django; django.setup(); from django.db import connection; connection.ensure_connection()"
```

**Redis connection error:**
```bash
# Check Redis is running
docker-compose ps redis

# Test connection
docker-compose exec redis redis-cli ping
```

**Static files not loading:**
```bash
# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

### 7.2 Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs web
docker-compose logs celery

# Follow logs
docker-compose logs -f
```

---

## 8. HTTPS/SSL (Production)

Update Caddyfile for production with real domain and Let's Encrypt:

```
api.elody-farm.md {
    reverse_proxy web:8000
    encode gzip
}
```

---

## 9. CI/CD (Future)

Example GitHub Actions workflow:

```yaml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build and deploy
        run: |
          docker-compose up -d --build
          docker-compose exec web python manage.py migrate
```

---

## 10. Health Checks

```bash
# API health
curl http://localhost/health/

# Database check
curl http://localhost/health/database/

# Redis check
curl http://localhost/health/redis/
```