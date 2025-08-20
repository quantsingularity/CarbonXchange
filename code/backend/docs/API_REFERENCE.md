# CarbonXchange API Reference

## Overview

The CarbonXchange API is a RESTful API that provides comprehensive functionality for carbon credit trading, portfolio management, and compliance monitoring. This document provides detailed information about all available endpoints, request/response formats, and authentication requirements.

## Base URL

```
Production: https://api.carbonxchange.com/v1
Staging: https://staging-api.carbonxchange.com/v1
Development: http://localhost:5000/api/v1
```

## Authentication

The API uses JWT (JSON Web Token) based authentication with access and refresh tokens.

### Authentication Flow

1. **Login** - Exchange credentials for tokens
2. **Access** - Use access token for API requests
3. **Refresh** - Use refresh token to get new access token
4. **Logout** - Invalidate tokens

### Token Types

- **Access Token**: Short-lived (1 hour) token for API access
- **Refresh Token**: Long-lived (30 days) token for obtaining new access tokens

### Headers

All authenticated requests must include:

```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data",
    "details": {
      "field": "email",
      "issue": "Invalid email format"
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_123456789"
  }
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 400 | Bad Request - Invalid request data |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 409 | Conflict - Resource already exists |
| 422 | Unprocessable Entity - Validation failed |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server error |

### Error Codes

| Code | Description |
|------|-------------|
| `AUTHENTICATION_FAILED` | Invalid credentials |
| `TOKEN_EXPIRED` | Access token has expired |
| `INSUFFICIENT_PERMISSIONS` | User lacks required permissions |
| `VALIDATION_ERROR` | Request data validation failed |
| `RESOURCE_NOT_FOUND` | Requested resource not found |
| `DUPLICATE_RESOURCE` | Resource already exists |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `COMPLIANCE_VIOLATION` | Action violates compliance rules |
| `INSUFFICIENT_BALANCE` | Insufficient account balance |
| `MARKET_CLOSED` | Trading market is closed |

## Authentication Endpoints

### POST /auth/register

Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1234567890",
  "company_name": "Example Corp",
  "country": "US",
  "timezone": "America/New_York"
}
```

**Response (201):**
```json
{
  "user": {
    "id": 1,
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "status": "pending_verification",
    "role": "individual",
    "created_at": "2024-01-15T10:30:00Z"
  },
  "tokens": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "Bearer",
    "expires_in": 3600
  }
}
```

### POST /auth/login

Authenticate user and receive access tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200):**
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "status": "active",
    "role": "individual",
    "last_login": "2024-01-15T10:30:00Z"
  },
  "tokens": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "Bearer",
    "expires_in": 3600
  }
}
```

### POST /auth/refresh

Refresh access token using refresh token.

**Headers:**
```http
Authorization: Bearer <refresh_token>
```

**Response (200):**
```json
{
  "tokens": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "Bearer",
    "expires_in": 3600
  }
}
```

### POST /auth/logout

Logout user and invalidate tokens.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "message": "Successfully logged out"
}
```

### GET /auth/me

Get current user information.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "user": {
    "id": 1,
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "status": "active",
    "role": "individual",
    "profile": {
      "first_name": "John",
      "last_name": "Doe",
      "phone_number": "+1234567890",
      "company_name": "Example Corp",
      "country": "US",
      "timezone": "America/New_York"
    },
    "kyc": {
      "status": "approved",
      "verification_level": 2,
      "approved_at": "2024-01-10T15:30:00Z"
    },
    "created_at": "2024-01-01T10:00:00Z",
    "last_login": "2024-01-15T10:30:00Z"
  }
}
```

## User Management Endpoints

### GET /users/profile

Get user profile information.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "profile": {
    "user_id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567890",
    "company_name": "Example Corp",
    "country": "US",
    "state_province": "NY",
    "city": "New York",
    "postal_code": "10001",
    "timezone": "America/New_York",
    "currency": "USD",
    "language": "en",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

### PUT /users/profile

Update user profile information.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1234567890",
  "company_name": "Example Corp",
  "country": "US",
  "state_province": "NY",
  "city": "New York",
  "postal_code": "10001",
  "timezone": "America/New_York"
}
```

**Response (200):**
```json
{
  "message": "Profile updated successfully",
  "profile": {
    "user_id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567890",
    "company_name": "Example Corp",
    "country": "US",
    "state_province": "NY",
    "city": "New York",
    "postal_code": "10001",
    "timezone": "America/New_York",
    "updated_at": "2024-01-15T11:00:00Z"
  }
}
```

### GET /users/kyc

Get KYC verification status.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "kyc": {
    "user_id": 1,
    "status": "approved",
    "verification_level": 2,
    "document_type": "passport",
    "document_number": "A12345678",
    "document_country": "US",
    "submitted_at": "2024-01-05T10:00:00Z",
    "approved_at": "2024-01-10T15:30:00Z",
    "expires_at": "2025-01-10T15:30:00Z",
    "notes": "All documents verified successfully"
  }
}
```

### POST /users/kyc

Submit KYC verification documents.

**Headers:**
```http
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request Body (Form Data):**
```
document_type: passport
document_number: A12345678
document_country: US
document_front: [file]
document_back: [file]
selfie: [file]
```

**Response (201):**
```json
{
  "message": "KYC documents submitted successfully",
  "kyc": {
    "user_id": 1,
    "status": "pending_review",
    "verification_level": 0,
    "document_type": "passport",
    "document_number": "A12345678",
    "document_country": "US",
    "submitted_at": "2024-01-15T11:00:00Z"
  }
}
```

## Carbon Credits Endpoints

### GET /carbon-credits/projects

Get list of carbon projects.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page` (integer): Page number (default: 1)
- `per_page` (integer): Items per page (default: 20, max: 100)
- `project_type` (string): Filter by project type
- `country` (string): Filter by country
- `status` (string): Filter by project status
- `vintage_year` (integer): Filter by vintage year
- `standard` (string): Filter by carbon standard
- `search` (string): Search in project name and description

**Response (200):**
```json
{
  "projects": [
    {
      "id": 1,
      "name": "Amazon Rainforest Conservation Project",
      "description": "Large-scale forest conservation project in Brazil",
      "project_type": "forestry",
      "status": "active",
      "country": "BR",
      "state_province": "Amazonas",
      "coordinates": {
        "latitude": -3.4653,
        "longitude": -62.2159
      },
      "total_credits": 1000000.0,
      "available_credits": 750000.0,
      "price_per_credit": 45.50,
      "vintage_year": 2023,
      "verification_standard": "VCS",
      "registry_id": "VCS-12345",
      "project_developer": "Green Earth Solutions",
      "verifier": "SCS Global Services",
      "methodology": "VM0015",
      "created_at": "2023-01-01T00:00:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

### GET /carbon-credits/projects/{project_id}

Get detailed information about a specific project.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "project": {
    "id": 1,
    "name": "Amazon Rainforest Conservation Project",
    "description": "Large-scale forest conservation project in Brazil focusing on preventing deforestation and promoting sustainable forest management practices.",
    "project_type": "forestry",
    "status": "active",
    "country": "BR",
    "state_province": "Amazonas",
    "coordinates": {
      "latitude": -3.4653,
      "longitude": -62.2159
    },
    "area_hectares": 50000.0,
    "total_credits": 1000000.0,
    "available_credits": 750000.0,
    "issued_credits": 250000.0,
    "retired_credits": 0.0,
    "price_per_credit": 45.50,
    "vintage_year": 2023,
    "verification_standard": "VCS",
    "registry_id": "VCS-12345",
    "project_developer": "Green Earth Solutions",
    "verifier": "SCS Global Services",
    "methodology": "VM0015",
    "project_documents": [
      {
        "type": "project_design_document",
        "url": "https://documents.carbonxchange.com/projects/1/pdd.pdf",
        "uploaded_at": "2023-01-01T00:00:00Z"
      }
    ],
    "monitoring_reports": [
      {
        "period": "2023-Q1",
        "url": "https://documents.carbonxchange.com/projects/1/monitoring-2023-q1.pdf",
        "uploaded_at": "2023-04-01T00:00:00Z"
      }
    ],
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

### GET /carbon-credits/credits

Get list of available carbon credits.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page` (integer): Page number (default: 1)
- `per_page` (integer): Items per page (default: 20, max: 100)
- `project_id` (integer): Filter by project ID
- `credit_type` (string): Filter by credit type
- `vintage_year` (integer): Filter by vintage year
- `status` (string): Filter by credit status
- `min_price` (float): Minimum price filter
- `max_price` (float): Maximum price filter

**Response (200):**
```json
{
  "credits": [
    {
      "id": 1,
      "project_id": 1,
      "serial_number": "VCS-12345-001-2023",
      "quantity": 1000.0,
      "vintage_year": 2023,
      "credit_type": "VCS",
      "status": "available",
      "price": 45.50,
      "currency": "USD",
      "issuance_date": "2023-06-01T00:00:00Z",
      "expiry_date": "2033-06-01T00:00:00Z",
      "project": {
        "id": 1,
        "name": "Amazon Rainforest Conservation Project",
        "project_type": "forestry",
        "country": "BR"
      },
      "create

