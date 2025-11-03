# SMS Authentication Setup Guide

## Phase 1: Docker & Backend Setup

### Step 1: Add Twilio Credentials

Add these variables to your root `.env` file:

```bash
# Twilio - SMS Authentication
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+15551234567
```

**Where to find these credentials:**
1. Go to https://console.twilio.com/
2. **Account SID** and **Auth Token**: Found on the dashboard homepage
3. **Phone Number**: Go to Phone Numbers → Manage → Active numbers

### Step 2: Rebuild API Container

Since `pyproject.toml` already includes `twilio>=8.0.0` and `phonenumbers>=8.13.0`, just rebuild:

```bash
# From project root
docker compose -f dev.yml up -d --build api
```

Wait for build to complete (~1-2 minutes).

### Step 3: Verify Setup

```bash
# Check all services are running
docker compose -f dev.yml ps

# Verify Redis is accessible
docker compose -f dev.yml exec redis redis-cli ping
# Expected output: PONG

# Verify Python dependencies installed
docker compose -f dev.yml exec api python -c "import twilio; import phonenumbers; print('✓ SMS dependencies installed')"
# Expected output: ✓ SMS dependencies installed

# Check API logs
docker compose -f dev.yml logs -f api
```

### Step 4: Test Backend Endpoints

```bash
# Test 1: Send SMS verification code
curl -X POST 'http://localhost/api/auth/sms/send' \
  -H 'Content-Type: application/json' \
  -d '{"phone": "+1YOUR_PHONE_NUMBER"}'

# Expected response:
# {
#   "message": "Verification code sent successfully",
#   "phone": "+1YOUR_PHONE_NUMBER",
#   "expires_in": 300
# }

# Check your phone for SMS with 6-digit code

# Test 2: Verify the code
curl -X POST 'http://localhost/api/auth/sms/verify' \
  -H 'Content-Type: application/json' \
  -d '{
    "phone": "+1YOUR_PHONE_NUMBER",
    "code": "123456"
  }'

# Expected response:
# {
#   "message": "Authentication successful",
#   "token": "1|eyJhbGc...",
#   "role": "user",
#   "user_id": 1,
#   "is_new_user": true
# }
```

### Step 5: Test Authenticated Request

```bash
# Use the token from step 4
curl -X GET 'http://localhost/api/user' \
  -H 'Authorization: Bearer 1|eyJhbGc...'

# Expected: Your user profile data
```

---

## Phase 2: Frontend Implementation

Frontend changes implemented in `/frontend/client/src/`:

### New Files Created:
1. **`entities/User/api/usePhoneAuth.ts`** - API calls for SMS auth
2. **`features/Auth/phone-login/model/usePhoneVerification.ts`** - State management
3. **`features/Auth/phone-login/ui/PhoneAuthInput.vue`** - Phone input & OTP UI
4. **`shared/ui/components/PhoneSignInButton.vue`** - Phone sign-in button

### Modified Files:
1. **`pages/index.vue`** - Added phone auth to home page
2. **`pages/login.vue`** - Added phone auth to login page

---

## Phase 3: Frontend Testing

### Test Flow on Home Page

1. Navigate to `http://localhost:3000`
2. Click "Sign in with Phone" button (should appear next to Google button)
3. Phone input field appears inline
4. Enter phone number in format: `+1234567890`
5. Click "Send Code"
6. Check phone for SMS (6-digit code)
7. Enter code in OTP input field
8. Click "Verify" or wait for auto-submit
9. Should be logged in and redirected

### Test Flow on Login Page

1. Navigate to `http://localhost:3000/login`
2. Scroll down past email/password form
3. Click "Sign in with Phone" button
4. Follow same flow as home page

### Test Error Cases

- **Invalid phone format**: Enter "123" → should show validation error
- **Wrong code**: Enter incorrect 6-digit code → should show "Invalid or expired code"
- **Expired code**: Wait 5+ minutes → code should expire
- **Resend code**: Click "Resend Code" → should send new SMS

---

## Troubleshooting

### SMS Not Received

1. **Check Twilio trial number limitations**:
   - Trial accounts can only send to verified phone numbers
   - Go to Twilio Console → Phone Numbers → Verified Caller IDs
   - Add your phone number if using trial account

2. **Check API logs for errors**:
   ```bash
   docker compose -f dev.yml logs -f api
   ```

3. **Verify Twilio credentials in .env**:
   - Ensure no extra spaces
   - Phone number must include country code (+1)

### Redis Connection Errors

```bash
# Check Redis is running
docker compose -f dev.yml ps redis

# Test Redis connection
docker compose -f dev.yml exec redis redis-cli ping

# Check Redis logs
docker compose -f dev.yml logs redis
```

### Frontend Not Showing Phone Auth

1. **Check browser console** for errors
2. **Clear browser cache** and reload
3. **Verify API is accessible**:
   ```bash
   curl http://localhost/api/health
   ```

---

## API Documentation

### POST /api/auth/sms/send

**Request:**
```json
{
  "phone": "+1234567890"
}
```

**Response (200 OK):**
```json
{
  "message": "Verification code sent successfully",
  "phone": "+1234567890",
  "expires_in": 300
}
```

**Errors:**
- **400**: Invalid phone number or Twilio error
- **422**: Validation error (phone format invalid)
- **500**: Server error

### POST /api/auth/sms/verify

**Request:**
```json
{
  "phone": "+1234567890",
  "code": "123456"
}
```

**Response (200 OK):**
```json
{
  "message": "Authentication successful",
  "token": "1|eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "role": "user",
  "user_id": 1,
  "is_new_user": true
}
```

**Errors:**
- **400**: Invalid or expired code
- **422**: Validation error (phone/code format)
- **500**: Server error

---

## Production Deployment Notes

### Environment Variables

For production (`prod.yml`), also set:
```bash
REDIS_PASSWORD=your_secure_redis_password
```

### Rebuild Production Containers

```bash
docker compose -f prod.yml up -d --build
docker compose -f prod.yml exec api alembic upgrade head
```

### Security Considerations

1. **Rate Limiting**: Consider adding rate limits to SMS endpoints (3-5 attempts per phone per hour)
2. **Phone Verification**: Validate phone numbers more strictly in production
3. **Redis Password**: Always use password in production (already configured in prod.yml)
4. **SMS Costs**: Monitor Twilio usage to avoid unexpected charges
5. **Fraud Prevention**: Consider implementing:
   - CAPTCHA before sending SMS
   - Phone number reputation checking
   - Velocity checks (# of codes per phone per day)

---

## Next Steps

After basic SMS auth is working, consider:

1. **SMS Notifications**: Send booking confirmations, payment alerts
2. **Two-Factor Auth**: Add SMS as 2FA option for email accounts
3. **Phone Number Management**: Let users add/change phone in profile
4. **International Support**: Better handling of international phone formats
5. **Retry Logic**: Auto-retry failed SMS sends
