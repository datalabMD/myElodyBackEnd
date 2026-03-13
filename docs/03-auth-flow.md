# Auth Flow — Elody-Farm Loyalty

## 1. Overview

The system uses JWT tokens with OTP (One-Time Password) for authentication:

- **Access Token**: 15 minutes
- **Refresh Token**: 7 days
- **OTP Code**: 6 digits, 5 minutes TTL, max 3 attempts

---

## 2. Login Flow (OTP)

### Step 1: Request OTP
```
Mobile App                    Backend
    |                            |
    |  POST /auth/request-login |
    |  {phone: "+37368988802"} |
    |-------------------------->|
    |                            |
    |  Generate 6-digit code    |
    |  Store in Redis (TTL 5m)  |
    |  Send SMS via provider    |
    |                            |
    |  {success: true, ...}     |
    |<--------------------------|
    |                            |
    v                            v
```

### Step 2: Login with OTP
```
Mobile App                    Backend
    |                            |
    |  POST /auth/login         |
    |  {phone, code: "123456"}  |
    |-------------------------->|
    |                            |
    |  Verify code in Redis     |
    |  If valid:                |
    |    - Mark OTP as used     |
    |    - Generate JWT tokens  |
    |    - Create session       |
    |  Return {access, refresh} |
    |                            |
    |  {access_token, ...}      |
    |<--------------------------|
    |                            |
    v                            v
```

### Token Storage (Mobile)
- **Access Token**: In-memory (flutter_secure_storage for backup)
- **Refresh Token**: flutter_secure_storage

---

## 3. Password Reset Flow

### Step 1: Request Reset
```
Mobile App                    Backend
    |                            |
    | POST /auth/request-       |
    |   password-reset          |
    | {phone: "+37368988802"}  |
    |-------------------------->|
    |                            |
    |  Check if user exists     |
    |  Generate OTP (reset)     |
    |  Store in Redis           |
    |  Send SMS                 |
    |                            |
    |  {success: true}          |
    |<--------------------------|
    |                            |
    v                            v
```

### Step 2: Verify OTP
```
Mobile App                    Backend
    |                            |
    |  POST /auth/verify-otp    |
    |  {phone, code: "123456"}  |
    |-------------------------->|
    |                            |
    |  Verify OTP               |
    |  Generate temp_token      |
    |  Store in Redis (10m TTL) |
    |                            |
    |  {valid: true,            |
    |   temp_token: "eyJ..."}   |
    |<--------------------------|
    |                            |
    v                            v
```

### Step 3: Set New Password
```
Mobile App                    Backend
    |                            |
    |  POST /auth/reset-password |
    |  {temp_token,             |
    |   new_password,           |
    |   confirm_password}       |
    |-------------------------->|
    |                            |
    |  Verify temp_token        |
    |  Validate password        |
    |  Update user password     |
    |  Invalidate all sessions  |
    |  Invalidate reset tokens  |
    |                            |
    |  {success: true}          |
    |<--------------------------|
    |                            |
    v                            v
```

---

## 4. Token Refresh Flow

```
Mobile App                    Backend
    |                            |
    |  POST /auth/refresh       |
    |  {refresh_token}         |
    |-------------------------->|
    |                            |
    |  Validate refresh token   |
    |  Check not blacklisted    |
    |  Generate new access +   |
    |    refresh tokens         |
    |  Blacklist old refresh    |
    |                            |
    |  {access_token,           |
    |   refresh_token,          |
    |   expires_in}            |
    |<--------------------------|
    |                            |
    v                            v
```

---

## 5. Logout Flow

```
Mobile App                    Backend
    |                            |
    |  POST /auth/logout        |
    |  Authorization: Bearer... |
    |-------------------------->|
    |                            |
    |  Blacklist access token   |
    |  Blacklist refresh token  |
    |  Clear session            |
    |                            |
    |  {success: true}          |
    |<--------------------------|
    |                            |
    v                            v
```

---

## 6. Rate Limiting

### Limits
| Endpoint | Limit |
|----------|-------|
| `/auth/request-login` | 5 requests / hour |
| `/auth/login` | 10 requests / minute |
| `/auth/request-password-reset` | 3 requests / hour |
| `/auth/verify-otp` | 5 requests / minute |
| `/auth/reset-password` | 5 requests / hour |

### Brute Force Protection
- After 5 failed login attempts: 15 minute lockout
- IP-based blocking via django-axes
- Account-based locking after 10 failed attempts

---

## 7. OTP Validation Rules

- **Length**: 6 digits
- **TTL**: 5 minutes
- **Max attempts**: 3 per code
- **Rate limit**: 5 requests per phone per hour
- **Format**: Only digits allowed

---

## 8. Password Requirements

- **Minimum length**: 8 characters
- **Must contain**:
  - At least 1 letter (a-z, A-Z)
  - At least 1 digit (0-9)
- **Recommended**: 1 special character
- **Case sensitive**: Yes
- **History**: Cannot reuse last 5 passwords

---

## 9. Security Headers

All responses include:
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

---

## 10. Error Codes

| Code | Description |
|------|-------------|
| `invalid_phone` | Invalid phone format |
| `invalid_code` | Invalid or expired OTP |
| `code_attempts_exceeded` | Too many failed attempts |
| `user_not_found` | User with this phone doesn't exist |
| `account_locked` | Account is locked |
| `password_too_weak` | Password doesn't meet requirements |
| `passwords_dont_match` | Passwords don't match |
| `token_expired` | Token has expired |
| `token_invalid` | Token is invalid |