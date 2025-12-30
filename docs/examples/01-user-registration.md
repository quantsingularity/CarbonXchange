# Example 1: User Registration and Authentication

This example demonstrates the complete user registration, KYC verification, and authentication process.

## Scenario

A new individual user wants to register on the platform, complete KYC verification, and start trading.

## Step 1: User Registration

```python
import requests

API_BASE = "http://localhost:5000/api"

# Register new user
registration_data = {
    "email": "jane.trader@example.com",
    "password": "SecureP@ss123",
    "full_name": "Jane Trader",
    "user_type": "individual",
    "phone": "+1234567890"
}

response = requests.post(f"{API_BASE}/auth/register", json=registration_data)
result = response.json()

print(f"Registration Status: {response.status_code}")
print(f"User ID: {result['user']['id']}")
print(f"Access Token: {result['access_token'][:20]}...")

# Save tokens for future requests
access_token = result['access_token']
refresh_token = result['refresh_token']
headers = {"Authorization": f"Bearer {access_token}"}
```

**Expected Output:**

```
Registration Status: 201
User ID: 1
Access Token: eyJhbGciOiJIUzI1NiIs...
```

## Step 2: Enable MFA (Optional but Recommended)

```python
# Enable MFA
response = requests.post(f"{API_BASE}/auth/mfa/enable", headers=headers)
mfa_data = response.json()

print(f"MFA QR Code: {mfa_data['qr_code'][:50]}...")
print(f"MFA Secret: {mfa_data['secret']}")

# User scans QR code with authenticator app
# Then verifies with TOTP code

verification_code = "123456"  # From authenticator app
response = requests.post(
    f"{API_BASE}/auth/mfa/verify",
    json={"code": verification_code},
    headers=headers
)

print(f"MFA Enabled: {response.status_code == 200}")
```

## Step 3: Submit KYC Documents

```python
# Submit KYC documents
kyc_data = {
    "document_type": "passport",
    "document_number": "P123456789",
    "country": "USA"
}

files = {
    'id_document': open('passport.pdf', 'rb'),
    'proof_of_address': open('utility_bill.pdf', 'rb')
}

response = requests.post(
    f"{API_BASE}/users/kyc/submit",
    data=kyc_data,
    files=files,
    headers=headers
)

print(f"KYC Submitted: {response.status_code}")
print(f"Status: {response.json()['status']}")  # pending_review
```

## Step 4: Check Profile Status

```python
# Check user profile
response = requests.get(f"{API_BASE}/users/profile", headers=headers)
profile = response.json()['user']

print(f"Email: {profile['email']}")
print(f"KYC Status: {profile['kyc_status']}")
print(f"Account Status: {profile['status']}")
print(f"Is Verified: {profile['is_verified']}")
print(f"MFA Enabled: {profile['mfa_enabled']}")
```

## Step 5: Login with MFA

```python
# Login (after KYC approval)
login_data = {
    "email": "jane.trader@example.com",
    "password": "SecureP@ss123"
}

response = requests.post(f"{API_BASE}/auth/login", json=login_data)
login_result = response.json()

if 'mfa_required' in login_result and login_result['mfa_required']:
    # MFA is enabled, need to provide code
    mfa_code = "456789"  # From authenticator app
    login_data['mfa_code'] = mfa_code

    response = requests.post(f"{API_BASE}/auth/login", json=login_data)
    login_result = response.json()

print("Login successful!")
print(f"New Access Token: {login_result['access_token'][:20]}...")
```

## Step 6: Refresh Token

```python
# When access token expires (after 15 minutes)
refresh_data = {"refresh_token": refresh_token}
response = requests.post(f"{API_BASE}/auth/refresh", json=refresh_data)

if response.status_code == 200:
    new_access_token = response.json()['access_token']
    headers = {"Authorization": f"Bearer {new_access_token}"}
    print("Token refreshed successfully!")
```

## Complete Script

```python
import requests
import time

class CarbonXchangeAuth:
    def __init__(self, api_base="http://localhost:5000/api"):
        self.api_base = api_base
        self.access_token = None
        self.refresh_token = None
        self.headers = {}

    def register(self, email, password, full_name, user_type="individual", phone=None):
        """Register a new user"""
        data = {
            "email": email,
            "password": password,
            "full_name": full_name,
            "user_type": user_type
        }
        if phone:
            data["phone"] = phone

        response = requests.post(f"{self.api_base}/auth/register", json=data)
        result = response.json()

        if response.status_code == 201:
            self.access_token = result['access_token']
            self.refresh_token = result['refresh_token']
            self._update_headers()
            return result['user']
        else:
            raise Exception(f"Registration failed: {result.get('error')}")

    def login(self, email, password, mfa_code=None):
        """Login existing user"""
        data = {"email": email, "password": password}
        if mfa_code:
            data["mfa_code"] = mfa_code

        response = requests.post(f"{self.api_base}/auth/login", json=data)
        result = response.json()

        if response.status_code == 200:
            self.access_token = result['access_token']
            self.refresh_token = result['refresh_token']
            self._update_headers()
            return result['user']
        elif 'mfa_required' in result:
            raise Exception("MFA code required")
        else:
            raise Exception(f"Login failed: {result.get('error')}")

    def _update_headers(self):
        """Update authorization headers"""
        self.headers = {"Authorization": f"Bearer {self.access_token}"}

    def get_profile(self):
        """Get user profile"""
        response = requests.get(
            f"{self.api_base}/users/profile",
            headers=self.headers
        )
        return response.json()['user']

# Usage
client = CarbonXchangeAuth()

# Register
user = client.register(
    email="jane.trader@example.com",
    password="SecureP@ss123",
    full_name="Jane Trader",
    user_type="individual",
    phone="+1234567890"
)

print(f"Registered user: {user['email']}")

# Check profile
profile = client.get_profile()
print(f"KYC Status: {profile['kyc_status']}")
```

## Next Steps

- See [Example 2](02-basic-trading.md) for trading operations
- Review [API Reference](../API.md) for complete endpoint documentation
- Check [Troubleshooting](../TROUBLESHOOTING.md) for common issues
