# Integration — Elody-Farm Loyalty

## 1. ERP Integration

### 1.1 Transaction Webhook

The ERP system sends transaction data to the webhook endpoint.

**Endpoint:**
```
POST /api/v1/webhooks/transaction
Authorization: Bearer <erp_api_key>
```

**Request Body:**
```json
{
  "transaction_id": "ERP-12345",
  "card_number": "2008926418709",
  "store_id": "store-uuid",
  "total_amount": 356.40,
  "bonus_earned": 17.82,
  "bonus_spent": 0,
  "items": [
    {
      "product_id": "PRD-001",
      "product_name": "Парацетамол 500мг",
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

**Security:**
- API key in header: `X-ERP-API-Key`
- IP whitelist for ERP servers
- Request validation

### 1.2 ERP Error Handling

| Status Code | Description | Action |
|-------------|-------------|--------|
| 200 | Success | Process transaction |
| 400 | Invalid data | Log error, return error details |
| 401 | Unauthorized | Return 401, log attempt |
| 409 | Duplicate | Check and update if needed |
| 500 | Server error | Retry with exponential backoff |

---

## 2. SMS Provider Integration

### 2.1 SMS Interface

```python
class SmsProvider(ABC):
    @abstractmethod
    def send(self, phone: str, message: str) -> SmsResult:
        pass
    
    @abstractmethod
    def get_balance(self) -> int:
        pass
```

### 2.2 Providers

#### Mock Provider (Development)
```python
class MockSmsProvider(SmsProvider):
    def send(self, phone: str, message: str):
        print(f"[MOCK SMS] To: {phone}, Message: {message}")
        return SmsResult(success=True, message_id="mock-123")
```

#### Infobip Provider
```python
class InfobipProvider(SmsProvider):
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
    
    def send(self, phone: str, message: str):
        response = requests.post(
            f"{self.base_url}/sms/2/text/single",
            headers={"Authorization": f"App {self.api_key}"},
            json={"to": phone, "text": message}
        )
        return SmsResult(
            success=response.status_code == 200,
            message_id=response.json().get("messages", [{}])[0].get("messageId")
        )
```

#### Twilio Provider
```python
class TwilioProvider(SmsProvider):
    def __init__(self, account_sid: str, auth_token: str):
        self.client = Client(account_sid, auth_token)
    
    def send(self, phone: str, message: str):
        result = self.client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone
        )
        return SmsResult(success=True, message_id=result.sid)
```

### 2.3 Usage

```python
from django.conf import settings

def send_sms(phone: str, message: str):
    provider = get_sms_provider()
    result = provider.send(phone, message)
    
    if not result.success:
        logger.error(f"SMS failed to {phone}: {result.error}")
    
    return result
```

---

## 3. Push Notifications

### 3.1 Firebase Cloud Messaging

```python
import firebase_admin
from firebase_admin import messaging

def send_push_notification(user: User, title: str, body: str, data: dict = None):
    if not user.profile.fcm_token:
        return
    
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        data=data or {},
        token=user.profile.fcm_token
    )
    
    response = messaging.send(message)
    return response
```

---

## 4. Email Integration

### 4.1 Email Providers

**Development:** Mailpit (local)
**Production:** SMTP (configurable)

### 4.2 Email Templates

```python
def send_welcome_email(user: User):
    template = get_template("emails/welcome.html")
    context = {"user": user}
    html_content = template.render(context)
    
    send_mail(
        subject="Добро пожаловать в Elody-Farm!",
        message=html_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_content
    )
```

---

## 5. File Storage

### 5.1 MinIO Configuration

```python
import minio

class FileStorage:
    def __init__(self):
        self.client = minio.Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
        )
    
    def upload_file(self, file, bucket, filename):
        self.client.put_object(
            bucket,
            filename,
            file,
            file.size,
            content_type=file.content_type
        )
        
        return f"{settings.MINIO_PUBLIC_URL}/{bucket}/{filename}"
```

### 5.2 Usage

- Avatars: `avatars/` bucket
- Receipts: `receipts/` bucket
- Promotion images: `promotions/` bucket

---

## 6. External APIs

### 6.1 Geocoding (for stores)

**Provider:** OpenStreetMap Nominatim (free) or Google Maps

```python
def get_coordinates(address: str):
    response = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={"q": address, "format": "json"}
    )
    data = response.json()
    
    if data:
        return {
            "lat": float(data[0]["lat"]),
            "lng": float(data[0]["lon"])
        }
```

### 6.2 Distance Calculation

```python
from math import radians, sin, cos, sqrt, atan2

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in km
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)² + cos(lat1) * cos(lat2) * sin(dlon/2)²
    c = 2 * atan2(√a, √(1-a))
    
    return R * c
```

---

## 7. Webhook Security

### 7.1 Signature Verification

```python
import hmac
import hashlib

def verify_webhook_signature(payload: bytes, signature: str, secret: str):
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected)
```

### 7.2 IP Whitelist

```python
ALLOWED_IPS = {
    'erp': ['10.0.0.0/8', '192.168.0.0/16'],
    'payment': ['203.0.113.0/24'],
}

def check_ip_whitelist(ip: str, service: str):
    for network in ALLOWED_IPS.get(service, []):
        if ip_in_network(ip, network):
            return True
    return False
```