# API Contract — Elody-Farm Loyalty

## Base URL
```
https://api.elody-farm.md/api/v1/
```

## Common Headers
```
Content-Type: application/json
Authorization: Bearer <access_token>
Accept-Language: ru|ro|en
```

## Authentication
- Access Token: JWT, expires in 15 minutes
- Refresh Token: JWT, expires in 7 days
- OTP: 6-digit code, expires in 5 minutes

---

## Endpoints

### 1. Auth API

#### 1.1 Request Login OTP
```http
POST /auth/request-login
```
**Request:**
```json
{
  "phone": "+37368988802"
}
```
**Response (200):**
```json
{
  "success": true,
  "message": "Код отправлен",
  "expires_in": 300
}
```

#### 1.2 Login with OTP
```http
POST /auth/login
```
**Request:**
```json
{
  "phone": "+37368988802",
  "code": "123456"
}
```
**Response (200):**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "Bearer",
  "expires_in": 900,
  "user": {
    "id": "uuid",
    "phone": "+37368988802",
    "email": "user@example.com"
  }
}
```

#### 1.3 Request Password Reset
```http
POST /auth/request-password-reset
```
**Request:**
```json
{
  "phone": "+37368988802"
}
```
**Response (200):**
```json
{
  "success": true,
  "message": "Код отправлен"
}
```

#### 1.4 Verify OTP
```http
POST /auth/verify-otp
```
**Request:**
```json
{
  "phone": "+37368988802",
  "code": "123456"
}
```
**Response (200):**
```json
{
  "valid": true,
  "temp_token": "eyJ..."
}
```

#### 1.5 Reset Password
```http
POST /auth/reset-password
```
**Request:**
```json
{
  "temp_token": "eyJ...",
  "new_password": "SecurePass123",
  "confirm_password": "SecurePass123"
}
```
**Response (200):**
```json
{
  "success": true,
  "message": "Пароль изменён"
}
```

#### 1.6 Logout
```http
POST /auth/logout
```
**Headers:** `Authorization: Bearer <access_token>`

**Response (200):**
```json
{
  "success": true,
  "message": "Вышел"
}
```

#### 1.7 Refresh Token
```http
POST /auth/refresh
```
**Request:**
```json
{
  "refresh_token": "eyJ..."
}
```
**Response (200):**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "expires_in": 900
}
```

---

### 2. Profile API

#### 2.1 Get Profile
```http
GET /profile
```
**Response (200):**
```json
{
  "id": "uuid",
  "phone": "+37368988802",
  "email": "user@example.com",
  "first_name": "Serghei",
  "last_name": "Romanciuc",
  "middle_name": "",
  "birth_date": "1987-01-04",
  "gender": "male",
  "avatar_url": "https://...",
  "loyalty_tier": "gold",
  "registered_at": "2024-01-01T00:00:00Z"
}
```

#### 2.2 Update Profile
```http
PATCH /profile
```
**Request:**
```json
{
  "first_name": "Serghei",
  "last_name": "Romanciuc",
  "middle_name": "",
  "birth_date": "1987-01-04",
  "gender": "male"
}
```
**Response (200):** Same as Get Profile

#### 2.3 Upload Avatar
```http
POST /profile/avatar
```
**Request:** Multipart form-data
```
avatar: <file>
```
**Response (200):**
```json
{
  "avatar_url": "https://cdn.elody-farm.md/avatars/uuid.jpg"
}
```

---

### 3. Loyalty API

#### 3.1 Get Card
```http
GET /loyalty/card
```
**Response (200):**
```json
{
  "card_number": "2008926418709",
  "barcode_type": "code128",
  "barcode_data": "2008926418709",
  "is_virtual": true,
  "has_physical_card": false,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### 3.2 Get Balance
```http
GET /loyalty/balance
```
**Response (200):**
```json
{
  "total_bonus": 125.50,
  "available_bonus": 110.00,
  "pending_bonus": 15.50,
  "expired_bonus": 0.00,
  "next_expiration_date": "2026-04-01T00:00:00Z",
  "tier": "gold",
  "tier_points": 1250,
  "next_tier_threshold": 2000
}
```

#### 3.3 Link Physical Card
```http
POST /loyalty/link-physical-card
```
**Request:**
```json
{
  "card_number": "2008926418708"
}
```
**Response (200):**
```json
{
  "success": true,
  "message": "Карта привязана",
  "card": { ... }
}
```

---

### 4. Transactions API

#### 4.1 Get Transactions List
```http
GET /transactions?page=1&limit=20&type=earned&date_from=2024-01-01&date_to=2024-12-31
```
**Query Parameters:**
- `page` (int): Page number
- `limit` (int): Items per page (max 100)
- `type` (str): Filter by type (earned/spent/all)
- `date_from` (date): Filter from date
- `date_to` (date): Filter to date

**Response (200):**
```json
{
  "items": [
    {
      "id": "uuid",
      "transaction_number": "TRX-10001",
      "date": "2026-03-10T14:45:00Z",
      "store_name": "Elody-Farm, Рышкановка",
      "total_amount": 356.40,
      "bonus_earned": 17.82,
      "bonus_spent": 0,
      "status": "completed"
    }
  ],
  "total": 100,
  "page": 1,
  "pages": 5
}
```

#### 4.2 Get Transaction Detail
```http
GET /transactions/{id}
```
**Response (200):**
```json
{
  "id": "uuid",
  "transaction_number": "TRX-10001",
  "date": "2026-03-10T14:45:00Z",
  "store": {
    "id": "uuid",
    "name": "Elody-Farm, Рышкановка",
    "address": "ул. Мир 15"
  },
  "total_amount": 356.40,
  "bonus_earned": 17.82,
  "bonus_spent": 0,
  "status": "completed",
  "items": [
    {
      "product_name": "Парацетамол 500мг",
      "quantity": 2,
      "unit_price": 25.00,
      "discount": 0,
      "total_price": 50.00,
      "is_promotional": false
    }
  ]
}
```

---

### 5. Promotions API

#### 5.1 Get Promotions
```http
GET /promotions?page=1&limit=20&type=promotion
```
**Query Parameters:**
- `type` (str): promotion or news

**Response (200):**
```json
{
  "items": [
    {
      "id": "uuid",
      "title": "Скидки на товары для детей",
      "subtitle": "До -25% в сети Elody-Farm",
      "image_url": "https://...",
      "start_date": "2026-03-01",
      "end_date": "2026-03-31",
      "type": "promotion"
    }
  ],
  "total": 10,
  "page": 1,
  "pages": 1
}
```

#### 5.2 Get Promotion Detail
```http
GET /promotions/{id}
```
**Response (200):**
```json
{
  "id": "uuid",
  "title": "Скидки на товары для детей",
  "subtitle": "До -25% в сети Elody-Farm",
  "description": "Подробное описание акции...",
  "image_url": "https://...",
  "start_date": "2026-03-01",
  "end_date": "2026-03-31",
  "type": "promotion",
  "category": "children",
  "participating_stores": [
    {
      "id": "uuid",
      "name": "Elody-Farm, Центр",
      "address": "ул. Мира 10"
    }
  ]
}
```

#### 5.3 Get News
```http
GET /news?page=1&limit=20
```
**Response (200):** Same structure as Promotions

---

### 6. Stores API

#### 6.1 Get Stores
```http
GET /stores?lat=47.0&lng=28.0&radius=5&search=аптека&page=1&limit=20
```
**Query Parameters:**
- `lat` (float): Latitude
- `lng` (float): Longitude
- `radius` (int): Radius in km
- `search` (str): Search by name/address
- `services` (str): Filter by services (24h,pickup)

**Response (200):**
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "Elody-Farm, Рышкановка",
      "address": "ул. Мира 15",
      "latitude": 47.0250,
      "longitude": 28.8500,
      "phone": "+37322123456",
      "distance": 0.5,
      "opening_hours": {
        "mon": "08:00-22:00",
        "tue": "08:00-22:00"
      },
      "services": {
        "24h": true,
        "pickup": true,
        "card_payment": true
      }
    }
  ],
  "total": 10,
  "page": 1,
  "pages": 1
}
```

#### 6.2 Get Store Detail
```http
GET /stores/{id}
```
**Response (200):** Same as list item with full details

---

### 7. Notifications API

#### 7.1 Get Notifications
```http
GET /notifications?page=1&limit=20
```
**Response (200):**
```json
{
  "items": [
    {
      "id": "uuid",
      "title": "Добро пожаловать!",
      "message": "Спасибо за регистрацию",
      "type": "system",
      "is_read": false,
      "sent_at": "2024-01-01T00:00:00Z"
    }
  ],
  "unread_count": 5,
  "total": 10,
  "page": 1,
  "pages": 1
}
```

#### 7.2 Mark as Read
```http
POST /notifications/{id}/read
```
**Response (200):**
```json
{
  "success": true
}
```

---

### 8. Surveys API

#### 8.1 Get Surveys
```http
GET /surveys?page=1&limit=20
```
**Response (200):**
```json
{
  "items": [
    {
      "id": "uuid",
      "title": "Оцените качество обслуживания",
      "description": "Помогите нам стать лучше",
      "reward_bonus": 20.00,
      "is_available": true,
      "is_completed": false,
      "starts_at": "2024-01-01",
      "ends_at": "2024-12-31"
    }
  ],
  "total": 5,
  "page": 1,
  "pages": 1
}
```

#### 8.2 Submit Survey
```http
POST /surveys/{id}/submit
```
**Request:**
```json
{
  "answers": {
    "question_1": "answer_value",
    "question_2": ["option1", "option2"]
  }
}
```
**Response (200):**
```json
{
  "success": true,
  "bonus_awarded": 20.00,
  "message": "Спасибо за участие!"
}
```

---

### 9. Settings API

#### 9.1 Get Settings
```http
GET /settings
```
**Response (200):**
```json
{
  "language": "ru",
  "notifications": {
    "push_enabled": true,
    "email_enabled": true,
    "sms_enabled": false,
    "marketing_enabled": true,
    "bonus_notifications": true
  }
}
```

#### 9.2 Update Language
```http
POST /settings/language
```
**Request:**
```json
{
  "language": "ro"
}
```
**Response (200):**
```json
{
  "success": true,
  "language": "ro"
}
```

#### 9.3 Update Notification Settings
```json
POST /settings/notifications
```
**Request:**
```json
{
  "push_enabled": true,
  "email_enabled": true,
  "marketing_enabled": false
}
```
**Response (200):** Same as Get Settings

#### 9.4 Delete Account
```http
DELETE /account
```
**Response (200):**
```json
{
  "success": true,
  "message": "Аккаунт удалён"
}
```

---

### 10. Webhooks

#### 10.1 Transaction Webhook (from ERP)
```http
POST /webhooks/transaction
```
**Request:**
```json
{
  "transaction_id": "ERP-12345",
  "card_number": "2008926418709",
  "store_id": "uuid",
  "total_amount": 356.40,
  "bonus_earned": 17.82,
  "bonus_spent": 0,
  "items": [
    {
      "product_id": "PRD-001",
      "product_name": "Парацетамол",
      "quantity": 2,
      "unit_price": 25.00,
      "discount": 0,
      "total_price": 50.00,
      "is_promotional": false
    }
  ],
  "timestamp": "2026-03-10T14:45:00Z"
}
```
**Response (200):**
```json
{
  "success": true,
  "transaction_id": "TRX-10001"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "validation_error",
  "message": "Ошибка валидации",
  "fields": {
    "phone": "Неверный формат телефона"
  }
}
```

### 401 Unauthorized
```json
{
  "error": "unauthorized",
  "message": "Необходима авторизация"
}
```

### 403 Forbidden
```json
{
  "error": "forbidden",
  "message": "Доступ запрещён"
}
```

### 404 Not Found
```json
{
  "error": "not_found",
  "message": "Ресурс не найден"
}
```

### 429 Too Many Requests
```json
{
  "error": "rate_limited",
  "message": "Слишком много запросов",
  "retry_after": 60
}
```

### 500 Internal Server Error
```json
{
  "error": "server_error",
  "message": "Внутренняя ошибка сервера"
}
```