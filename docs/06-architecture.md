# Architecture — Elody-Farm Loyalty

## 1. Project Structure

```
elody-farm-backend/
├── config/                 # Django settings
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   ├── wsgi.py
│   └── celery.py
├── apps/                   # Django apps
│   ├── users/             # User management
│   ├── authn/             # Authentication
│   ├── loyalty/           # Loyalty system
│   ├── transactions/      # Transactions
│   ├── promotions/       # Promotions & news
│   ├── stores/           # Pharmacy stores
│   ├── notifications/    # Notifications
│   ├── surveys/          # Surveys
│   ├── settings/         # User settings
│   ├── webhooks/        # ERP webhooks
│   └── api/
│       └── v1/           # Django Ninja API
├── core/                  # Shared code
│   ├── models.py
│   ├── validators.py
│   ├── exceptions.py
│   └── permissions.py
├── services/              # Business logic
│   ├── sms.py
│   ├── bonus.py
│   ├── notifications.py
│   └── erp.py
├── tasks/                 # Celery tasks
├── management/
│   └── commands/         # Custom commands
├── tests/                 # Tests
├── docs/                  # Documentation
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

---

## 2. Architecture Layers

### 2.1 Presentation Layer (API)
- **Django Ninja** for REST API
- Schema validation with Pydantic
- OpenAPI/Swagger documentation

### 2.2 Business Logic Layer (Services)
- Service classes for business logic
- Decoupled from Django models
- Easy to test and modify

### 2.3 Data Layer (Models)
- Django ORM models
- Simple History for audit trail
- UUID primary keys

---

## 3. Technology Stack

### Backend
| Component | Technology |
|-----------|------------|
| Framework | Django 5.x |
| API | Django Ninja |
| Database | PostgreSQL |
| Cache/Queue | Redis |
| Task Queue | Celery + Celery Beat |
| Auth | JWT (simplejwt) |
| WebSocket | Django Channels |

### Infrastructure
| Component | Technology |
|-----------|------------|
| Web Server | Caddy |
| Storage | MinIO (S3) |
| Email | Mailpit (dev) |
| Container | Docker Compose |

---

## 4. API Design

### 4.1 Response Format

**Success Response:**
```json
{
  "success": true,
  "data": { ... }
}
```

**Paginated Response:**
```json
{
  "items": [ ... ],
  "total": 100,
  "page": 1,
  "pages": 5
}
```

**Error Response:**
```json
{
  "error": "error_code",
  "message": "Human readable message",
  "fields": { ... }  // optional, for validation errors
}
```

### 4.2 Status Codes

| Code | Usage |
|------|-------|
| 200 | OK |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Error |
| 429 | Rate Limited |
| 500 | Server Error |

---

## 5. Database Design

### 5.1 Indexes

```python
class Transaction(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['user', 'transaction_date']),
            models.Index(fields=['status']),
            models.Index(fields=['store', 'transaction_date']),
        ]
```

### 5.2 Migrations

- All migrations in `apps/<app>/migrations/`
- Use `simple_history` for audit trail
- Run migrations in Docker startup

---

## 6. Security

### 6.1 Authentication
- JWT tokens (15 min access, 7 day refresh)
- OTP for sensitive operations
- Rate limiting on auth endpoints

### 6.2 Authorization
- Permissions classes per endpoint
- Object-level permissions where needed

### 6.3 Data Protection
- Password hashing (PBKDF2)
- CSRF protection
- XSS protection
- SQL injection prevention (ORM)

---

## 7. Performance

### 7.1 Caching Strategy

| Data | Cache TTL | Invalidation |
|------|-----------|--------------|
| User profile | 5 min | On update |
| Loyalty balance | 1 min | On transaction |
| Promotions | 15 min | On create/update |
| Stores | 1 hour | On create/update |

### 7.2 Query Optimization

- Select_related for FK
- Prefetch_related for M2M
- Pagination for lists
- Database indexes

---

## 8. Deployment

### 8.1 Docker Services

```yaml
services:
  postgres:
    image: postgres:16
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
  
  web:
    build: .
    command: gunicorn config.asgi:application
    depends_on: [postgres, redis]
  
  celery:
    command: celery -A config worker -l info
    depends_on: [redis, postgres]
  
  celery-beat:
    command: celery -A config beat -l info
    depends_on: [redis, postgres]
```

### 8.2 Environment Variables

See `.env.example` for all required variables.

---

## 9. Monitoring

### 9.1 Health Checks

- `/health/` - Basic health (DB, Redis)
- `/health/liveness/` - Kubernetes liveness
- `/health/readiness/` - Kubernetes readiness

### 9.2 Logging

- Django logging to stdout
- JSON format for production
- Log levels: DEBUG, INFO, WARNING, ERROR

---

## 10. Testing

### 10.1 Test Structure

```
tests/
├── unit/
│   └── tests/
│       ├── test_bonus_calculation.py
│       └── test_otp_generation.py
├── integration/
│   └── tests/
│       ├── test_auth_flow.py
│       └── test_promotions_api.py
└── conftest.py
```

### 10.2 Running Tests

```bash
pytest                    # Run all tests
pytest --cov              # With coverage
pytest -k test_auth       # Filter by name
```