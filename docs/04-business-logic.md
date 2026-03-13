# Business Logic — Elody-Farm Loyalty

## 1. Bonus System

### 1.1 Bonus Calculation

**Formula:**
```
bonus_earned = round(total_amount * bonus_rate, 2)
```

**Default Rate:** 5% (configurable in BonusSettings)

**Example:**
```
Check total: 356.40 MDL
Bonus rate: 5%
Bonus earned: round(356.40 * 0.05, 2) = 17.82
```

### 1.2 Bonus Spending

- **Minimum to spend:** 10.00 MDL (configurable)
- **Partial spending:** Allowed
- **Rounding:** Round to 2 decimal places

**Example:**
```
Available: 125.50
Spent: 50.00
Remaining: 75.50
```

### 1.3 Bonus Expiration

**Rules:**
- Expiration period: 12 months (configurable)
- Each bonus entry has its own expiration date
- Expired bonuses are moved to `expired_bonus` balance

**Expiration Process (Celery Task):**
```
1. Query all BonusLedger entries where:
   - type = 'earned'
   - expires_at <= now()
   - is_expired = False

2. For each entry:
   - Create new BonusLedger with type='expired'
   - Mark original as expired
   
3. Update user's available_bonus
```

### 1.4 Bonus Balance Calculation

```python
def get_balance(user):
    earned = BonusLedger.objects.filter(
        user=user, type='earned'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    spent = BonusLedger.objects.filter(
        user=user, type='spent'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    expired = BonusLedger.objects.filter(
        user=user, type='expired'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    bonus = BonusLedger.objects.filter(
        user=user, type='bonus'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    return {
        'total': earned + bonus,
        'available': earned + bonus - spent - expired,
        'pending': 0,  # Future: bonus awaiting confirmation
        'expired': expired
    }
```

---

## 2. Loyalty Tiers

### 2.1 Tier Levels

| Tier | Monthly Spend Threshold | Bonus Multiplier |
|------|----------------------|------------------|
| Bronze | 0 - 499 MDL | 1x |
| Silver | 500 - 1499 MDL | 1.25x |
| Gold | 1500 - 2999 MDL | 1.5x |
| Platinum | 3000+ MDL | 2x |

### 2.2 Tier Calculation

```python
def calculate_tier(user):
    # Calculate total spent in last 12 months
    total = Transaction.objects.filter(
        user=user,
        status='completed',
        transaction_date__gte=timezone.now() - timedelta(days=365)
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    if total >= 3000:
        return 'platinum'
    elif total >= 1500:
        return 'gold'
    elif total >= 500:
        return 'silver'
    else:
        return 'bronze'
```

### 2.3 Tier Upgrade/Downgrade

- Checked daily at 2:00 AM (Celery)
- Notification sent on tier change
- Bonus multiplier applied to new purchases

---

## 3. Birthday Bonus

**Rules:**
- Users with birth_date get bonus on birthday
- Bonus amount: Configurable (default 50 MDL)
- Can be disabled per user

**Process (Celery Task):**
```python
def send_birthday_bonuses():
    today = date.today()
    users = CustomerProfile.objects.filter(
        birth_date__month=today.month,
        birth_date__day=today.day,
        user__is_active=True
    )
    
    for profile in users:
        BonusLedger.objects.create(
            user=profile.user,
            type='bonus',
            amount=settings.BIRTHDAY_BONUS_AMOUNT,
            description='Бонус ко дню рождения',
            expires_at=date.today() + timedelta(days=30)
        )
```

---

## 4. Card Linking

### 4.1 Virtual Card

- Created automatically on user registration
- Card number format: `2` + 10 digits (e.g., `2008926418709`)
- Barcode type: Code128

### 4.2 Physical Card Linking

```python
def link_physical_card(user, card_number):
    # Check card exists
    card = LoyaltyCard.objects.filter(
        card_number=card_number,
        is_virtual=False
    ).first()
    
    if not card:
        raise ValidationError("Карта не найдена")
    
    if card.user:
        raise ValidationError("Карта уже привязана")
    
    # Link to user
    card.user = user
    card.save()
    
    # Update virtual card
    virtual_card = LoyaltyCard.objects.filter(
        user=user, is_virtual=True
    ).first()
    virtual_card.has_physical_card = True
    virtual_card.save()
    
    return card
```

---

## 5. Transaction Processing

### 5.1 From ERP Webhook

```python
def process_transaction(data):
    # Find user by card number
    card = LoyaltyCard.objects.filter(
        card_number=data['card_number']
    ).first()
    
    if not card:
        raise ValidationError("Карта не найдена")
    
    # Create transaction
    transaction = Transaction.objects.create(
        user=card.user,
        store_id=data['store_id'],
        transaction_number=f"TRX-{data['transaction_id']}",
        total_amount=data['total_amount'],
        bonus_earned=data.get('bonus_earned', 0),
        bonus_spent=data.get('bonus_spent', 0),
        status='completed',
        transaction_date=data['timestamp'],
        erp_id=data['transaction_id']
    )
    
    # Create items
    for item in data['items']:
        TransactionItem.objects.create(
            transaction=transaction,
            product_id=item['product_id'],
            product_name=item['product_name'],
            quantity=item['quantity'],
            unit_price=item['unit_price'],
            discount=item.get('discount', 0),
            total_price=item['total_price'],
            is_promotional=item.get('is_promotional', False)
        )
    
    # Create bonus ledger entry
    if transaction.bonus_earned > 0:
        settings = BonusSettings.objects.first()
        BonusLedger.objects.create(
            user=card.user,
            transaction=transaction,
            type='earned',
            amount=transaction.bonus_earned,
            description=f"Покупка в {transaction.store.name}",
            expires_at=timezone.now() + timedelta(
                days=settings.expiration_months * 30
            )
        )
    
    return transaction
```

---

## 6. Notification System

### 6.1 Notification Types

| Type | Description | Channels |
|------|-------------|----------|
| system | System messages | Push, Email |
| marketing | Promotions, news | Push, Email, SMS (opt-in) |
| bonus | Balance changes | Push, Email |
| transaction | Purchase confirmations | Push, Email |

### 6.2 Creating Notifications

```python
def create_notification(user, notification_type, title, message):
    notification = Notification.objects.create(
        user=user,
        type=notification_type,
        title=title,
        message=message
    )
    
    # Check user preferences
    settings = user.notification_settings
    
    if notification_type == 'system' and settings.push_enabled:
        send_push(user, notification)
    elif notification_type == 'marketing' and settings.marketing_enabled:
        send_marketing(user, notification)
    # ...
    
    return notification
```

---

## 7. Survey System

### 7.1 Survey Eligibility

```python
def get_available_surveys(user):
    profile = user.profile
    
    return Survey.objects.filter(
        is_active=True,
        starts_at__lte=timezone.now(),
        ends_at__gte=timezone.now()
    ).exclude(
        answers__user=user
    ).filter(
        target_tiers__contains=[profile.loyalty_tier]
    )
```

### 7.2 Survey Completion

```python
def submit_survey(survey, user, answers):
    # Validate answers
    for question in survey.questions:
        if question.is_required and question.id not in answers:
            raise ValidationError(f"Question {question.id} is required")
    
    # Save answers
    answer = SurveyAnswer.objects.create(
        survey=survey,
        user=user,
        answers=answers
    )
    
    # Award bonus
    if survey.reward_bonus > 0:
        BonusLedger.objects.create(
            user=user,
            type='bonus',
            amount=survey.reward_bonus,
            description=f"Опрос: {survey.title}"
        )
    
    return answer
```