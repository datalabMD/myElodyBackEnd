# Data Models — Elody-Farm Loyalty

## 1. Core Models

### UUIDModel
Base model providing UUID primary key for all models.

### TimeStampedModel
- `created_at` — Auto created timestamp
- `updated_at` — Auto updated timestamp

---

## 2. Users App

### User
```python
class User(AbstractBaseUser, UUIDModel, TimeStampedModel):
    id: UUID          # Primary key
    phone: str        # +37368988802 (unique)
    email: str        # user@example.com (unique, nullable)
    password: str     # Hashed password
    is_active: bool   # Account status
    is_staff: bool    # Admin access
    created_at: datetime
    updated_at: datetime
```

### CustomerProfile
```python
class CustomerProfile(UUIDModel, TimeStampedModel):
    id: UUID
    user: FK(User) → OneToOne
    
    first_name: str           # Имя
    last_name: str           # Фамилия
    middle_name: str         # Отчество
    birth_date: date         # Дата рождения
    gender: str              # male/female/other
    avatar: ImageField       # Аватар
    status: str              # active/inactive/suspended
    loyalty_tier: str        # bronze/silver/gold/platinum
    registered_at: datetime # Дата регистрации
    
    created_at: datetime
    updated_at: datetime
```

---

## 3. Authn App

### OTP
```python
class OTP(UUIDModel, TimeStampedModel):
    id: UUID
    phone: str              # +37368988802
    code: str              # 6-digit code
    purpose: str           # login/password_reset
    attempts: int           # Failed attempts count
    is_used: bool           # Code used flag
    expires_at: datetime    # Expiration time
    ip_address: str        # Client IP
```

### PasswordResetToken
```python
class PasswordResetToken(UUIDModel, TimeStampedModel):
    id: UUID
    user: FK(User)
    token: str              # Unique token
    is_used: bool
    expires_at: datetime
    ip_address: str
```

---

## 4. Loyalty App

### LoyaltyCard
```python
class LoyaltyCard(UUIDModel, TimeStampedModel):
    id: UUID
    user: FK(User)
    card_number: str        # Unique card number
    barcode_type: str       # code128/qr/ean13
    is_virtual: bool       # Virtual vs physical
    has_physical_card: bool # Has physical card
    is_active: bool
    
    created_at: datetime
    updated_at: datetime
```

### BonusLedger
```python
class BonusLedger(UUIDModel, TimeStampedModel):
    id: UUID
    user: FK(User)
    transaction: FK(Transaction) → nullable
    amount: Decimal          # +/-
    type: str               # earned/spent/expired/adjusted/bonus
    description: str
    expires_at: datetime     # Expiration date for earned
    
    created_at: datetime
    updated_at: datetime
```

### BonusSettings
```python
class BonusSettings(TimeStampedModel):
    bonus_rate: Decimal       # 5.0 (%)
    expiration_months: int   # 12 (months)
    min_bonus_to_spend: Decimal # 10.0
```

---

## 5. Transactions App

### Transaction
```python
class Transaction(UUIDModel, TimeStampedModel):
    id: UUID
    user: FK(User)
    store: FK(Store)
    
    transaction_number: str  # TRX-XXXXX
    total_amount: Decimal    # Total check amount
    bonus_earned: Decimal    # Earned bonuses
    bonus_spent: Decimal     # Spent bonuses
    status: str             # pending/completed/refunded/cancelled
    receipt_url: str        # URL to receipt
    transaction_date: datetime
    erp_id: str             # External ERP ID
    
    created_at: datetime
    updated_at: datetime
```

### TransactionItem
```python
class TransactionItem(UUIDModel):
    id: UUID
    transaction: FK(Transaction)
    product_id: str
    product_name: str
    quantity: int
    unit_price: Decimal
    discount: Decimal
    total_price: Decimal
    promotion: FK(Promotion) → nullable
    is_promotional: bool
```

---

## 6. Promotions App

### Promotion
```python
class Promotion(UUIDModel, TimeStampedModel):
    id: UUID
    title: str
    subtitle: str
    description: str
    image_url: str
    start_date: date
    end_date: date
    type: str           # promotion/news
    category: str
    is_active: bool
    participating_stores: M2M(Store)
    
    created_at: datetime
    updated_at: datetime
```

### NewsItem
```python
class NewsItem(UUIDModel, TimeStampedModel):
    id: UUID
    title: str
    subtitle: str
    content: str
    image_url: str
    published_at: datetime
    is_active: bool
    
    created_at: datetime
    updated_at: datetime
```

---

## 7. Stores App

### Store
```python
class Store(UUIDModel, TimeStampedModel):
    id: UUID
    name: str
    address: str
    latitude: Decimal
    longitude: Decimal
    phone: str
    opening_hours: JSON     # {"mon": "08:00-22:00", ...}
    services: JSON          # {"24h": true, "pickup": true, ...}
    is_active: bool
    
    created_at: datetime
    updated_at: datetime
```

---

## 8. Notifications App

### Notification
```python
class Notification(UUIDModel, TimeStampedModel):
    id: UUID
    user: FK(User)
    title: str
    message: str
    type: str              # system/marketing/bonus
    is_read: bool
    sent_at: datetime
    read_at: datetime      # nullable
    
    created_at: datetime
    updated_at: datetime
```

### UserNotificationSettings
```python
class UserNotificationSettings(UUIDModel):
    id: UUID
    user: FK(User) → OneToOne
    push_enabled: bool
    email_enabled: bool
    sms_enabled: bool
    marketing_enabled: bool
    bonus_notifications: bool
```

---

## 9. Surveys App

### Survey
```python
class Survey(UUIDModel, TimeStampedModel):
    id: UUID
    title: str
    description: str
    reward_bonus: Decimal
    is_active: bool
    starts_at: datetime
    ends_at: datetime
    target_tiers: JSON      # ["bronze", "silver"]
```

### SurveyQuestion
```python
class SurveyQuestion(UUIDModel):
    id: UUID
    survey: FK(Survey)
    order: int
    question_text: str
    question_type: str     # single_choice/multiple_choice/text
    options: JSON          # ["Option 1", "Option 2", ...]
    is_required: bool
```

### SurveyAnswer
```python
class SurveyAnswer(UUIDModel):
    id: UUID
    survey: FK(Survey)
    user: FK(User)
    answers: JSON          # {"question_id": "answer_value"}
    submitted_at: datetime
```

---

## 10. Settings App

### UserSettings
```python
class UserSettings(UUIDModel):
    id: UUID
    user: FK(User) → OneToOne
    language: str          # ru/ro/en
    currency: str          # MDL
```

---

## Relationships Diagram

```
User (1) ─── (1) CustomerProfile
User (1) ─── (*) LoyaltyCard
User (1) ─── (*) BonusLedger
User (1) ─── (*) Transaction
User (1) ─── (*) Notification
User (1) ─── (*) SurveyAnswer

User (1) ─── (1) UserSettings
User (1) ─── (1) UserNotificationSettings

Transaction (1) ─── (*) TransactionItem

Store (1) ─── (*) Transaction
Store (1) ─── (*) Promotion (M2M)

Promotion (1) ─── (*) TransactionItem

Survey (1) ─── (*) SurveyQuestion
Survey (1) ─── (*) SurveyAnswer
```