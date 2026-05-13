# IP Australia API Endpoints Research

**Last Updated:** 2026-05-13  
**Source:** https://descriptions.api.gov.au (API description pages) + https://portal.api.ipaustralia.gov.au (Developer Portal)

---

## Overview

IP Australia provides OAuth 2.0-protected REST APIs for searching and managing Australian intellectual property (Trademarks, Designs, Patents). Documentation is split between a description portal (with basic endpoint definitions) and a Salesforce-hosted developer portal (with full specifications).

**Key Finding:** Public documentation is minimal; detailed request/response schemas require accessing the developer portal with credentials.

---

## Authentication

All APIs use OAuth 2.0 with Client Credentials grant (B2B partner flow).

### Token Endpoint

**Test Environment:**
```
POST https://test.api.ipaustralia.gov.au/public/external-token-api/v1/access_token
```

**Production Environment:**
```
POST https://production.api.ipaustralia.gov.au/public/external-token-api/v1/access_token
```

### Token Request Format

```
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials
client_id={CLIENT_ID}
client_secret={CLIENT_SECRET}
```

### Token Response

```json
{
  "access_token": "eyJraWQiOi...[JWT]...A",
  "expires_in": 3600,
  "token_type": "Bearer"
}
```

### Using the Token

Include in all API requests:
```
Authorization: Bearer {access_token}
```

Token TTL: 1 hour (reusable across multiple requests)

---

## API 1: Australian Trade Mark Search API

### Base URLs

**Test:**
```
https://test.api.ipaustralia.gov.au/public/australian-trade-mark-search-api/v1/
```

**Production:**
```
https://production.api.ipaustralia.gov.au/public/australian-trade-mark-search-api/v1/
```

### Endpoints

#### 1.1 Quick Search

**Path:** `POST /search/quick`

**Description:** Search for Trade Marks matching given criteria (query string, type, status, update date filter).

**Request Payload (Example from docs):**
```json
{
  "query": "TEST",
  "sort": {
    "field": "NUMBER",
    "direction": "ASCENDING"
  },
  "filters": {
    "quickSearchType": [
      "WORD"
    ],
    "status": [
      "REGISTERED"
    ]
  },
  "changedSinceDate": "2019-01-15"
}
```

**Request Field Definitions (Inferred from example):**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | string | Yes | Search query string |
| `sort.field` | enum | No | Sort field (e.g., "NUMBER") |
| `sort.direction` | enum | No | "ASCENDING" or "DESCENDING" |
| `filters.quickSearchType` | array[enum] | No | Filter by search type (e.g., "WORD") |
| `filters.status` | array[enum] | No | Filter by status (e.g., "REGISTERED") |
| `changedSinceDate` | string (date) | No | ISO date; return only marks updated since |

**Response Format:** JSON array of Trade Mark Numbers + metadata (detailed schema unavailable in public docs)

**Pagination:** Not specified in public docs

---

#### 1.2 Get Trade Mark by Number

**Path:** `GET /trade-mark/{ipRightIdentifier}`

**Description:** Retrieve all public information for a single Trade Mark by its IP right identifier (Trade Mark Number).

**Path Parameters:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `ipRightIdentifier` | string | Yes | The Trade Mark number (e.g., "1234567") |

**Query Parameters:** None specified in public docs

**Response Format:** JSON object containing full Trade Mark details (detailed schema unavailable in public docs)

---

### Trade Mark API Notes

- **Response Format:** All responses are JSON.
- **Full API Spec:** For complete request/response schemas, users must access https://portal.api.ipaustralia.gov.au/s/ with developer credentials.
- **OAuth Scopes:** Scope observed in example token: `https://api.ipaustralia.gov.au/b2b/iprights/agent`

---

## API 2: Australian Design Search API

### Base URLs

**Test:**
```
https://test.api.ipaustralia.gov.au/public/australian-design-search-api/v1/
```

**Production:**
```
https://production.api.ipaustralia.gov.au/public/australian-design-search-api/v1/
```

### Endpoints

#### 2.1 Quick Search

**Path:** `POST /search/quick`

**Description:** Search for Australian Designs matching given criteria (query string, classification filter, status filter, update date).

**Request Payload (Example from docs):**
```json
{
  "changedSinceDate": "2001-10-01",
  "filters": {
    "classificationFilter": [
      "0202c"
    ],
    "statusFilter": [
      "REGISTERED"
    ]
  },
  "query": "clothing"
}
```

**Request Field Definitions (Inferred from example):**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | string | Yes | Search query string |
| `filters.classificationFilter` | array[string] | No | Filter by design classification codes (e.g., "0202c") |
| `filters.statusFilter` | array[enum] | No | Filter by status (e.g., "REGISTERED") |
| `changedSinceDate` | string (date) | No | ISO date; return only designs updated since |

**Response Format:** JSON array of Design Numbers + metadata (detailed schema unavailable in public docs)

**Pagination:** Not specified in public docs

---

#### 2.2 Get Design by Number

**Path:** `GET /design/{ipRightIdentifier}`

**Description:** Retrieve all public information for a single Design by its IP right identifier (Design Number).

**Path Parameters:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `ipRightIdentifier` | string | Yes | The Design number (e.g., "1234567") |

**Query Parameters:** None specified in public docs

**Response Format:** JSON object containing full Design details (detailed schema unavailable in public docs)

---

### Design API Notes

- **Response Format:** All responses are JSON.
- **Full API Spec:** For complete request/response schemas, users must access https://portal.api.ipaustralia.gov.au/s/ with developer credentials.
- **OAuth Scopes:** Same as Trade Mark API; scope: `https://api.ipaustralia.gov.au/b2b/iprights/agent`

---

## API 3: Patent Search API

### Status

**404 Page Not Found** – https://descriptions.api.gov.au/ipaustralia/patent-search/ returns a 404. This endpoint is either:
- Still under development
- Not yet published to public documentation
- Moved to a different URL

### Alternative: IP Right Management (B2B) API

Based on example code in the Trade Mark and Design documentation pages, IP Australia also provides a **Patent/IP Right Management API** (hint from sample request path):

**Sample Endpoint Observed:**
```
POST https://test.api.ipaustralia.gov.au/public/ipright-management-b2b-api/v1/patents/{patentNumber}/renew
```

**Request Payload (Example from docs):**
```json
{
  "submitterReference": "MyPatentRenewal",
  "numOfYearsToRenew": "1"
}
```

This suggests a management API exists but is **not publicly documented in the description portal**. Full endpoint list requires access to the developer portal.

---

## Discovered Endpoints Summary

| API | Search | Get Details | Additional Ops | Total |
|-----|--------|-------------|-----------------|-------|
| Trade Marks | 1 (POST /search/quick) | 1 (GET /{id}) | — | **2** |
| Designs | 1 (POST /search/quick) | 1 (GET /{id}) | — | **2** |
| Patents | — | — | 1 (renew endpoint hint) | **1 (partial)** |

**Total Publicly Documented Endpoints: 5**

---

## Known Limitations

### Public Documentation Gaps

1. **No OpenAPI/Swagger specs publicly available.** Attempts to fetch `swagger.json`, `openapi.json`, etc. return 404.
2. **Minimal request/response schemas.** The description portal only provides one example payload per endpoint; actual field constraints (required, types, nested structures, enums) are not detailed.
3. **No pagination documentation.** Search endpoints don't specify limit/offset or cursor-based pagination behavior.
4. **Patents API not published.** Patent search endpoint is missing; only a renewal operation is hinted at in example code.
5. **Rate limits not documented.** No published rate-limit headers or thresholds mentioned.
6. **Error response formats not specified.** No example error payloads shown.

### What Requires Developer Portal Access

- Detailed field schemas for request/response payloads
- Complete list of enum values (e.g., valid statuses, search types, classification codes)
- Pagination parameters and behavior
- Full Patent Search API endpoints
- Rate limiting policies
- Support for authorization code grant (user-level tokens, planned for future)
- Sandbox/test environment API keys

---

## Build Assessment

### Buildable from Public Docs

- **Basic OAuth 2.0 token fetching** – Fully documented.
- **Trade Mark quick search endpoint** – Path and one example payload provided; enough to build a basic implementation with placeholder schema validation.
- **Trade Mark detail fetch endpoint** – Path and path parameter defined.
- **Design quick search endpoint** – Path and one example payload provided.
- **Design detail fetch endpoint** – Path and path parameter defined.

### Requires Sandbox Account / Portal Access

- **Type-safe request/response models** – Without OpenAPI specs or detailed schemas, field validation is guesswork.
- **Pagination** – No public docs on limit, offset, cursor, or total_count patterns.
- **Patents API** – Completely undocumented in public portal.
- **Error handling** – No example error responses.
- **Enum validation** – Valid statuses, classification codes, search types are not listed.
- **Rate-limit handling** – No headers published.
- **Advanced features** – Any complex filtering, sorting, or aggregation beyond the one example per endpoint.

---

## Next Steps for Client Development

1. **Request developer portal access** at https://portal.api.ipaustralia.gov.au/s/ or email MDB-TDS@ipaustralia.gov.au.
2. **Download OpenAPI spec** from the portal (if available as downloadable file).
3. **Contact IP Australia** for:
   - Patents API documentation
   - Complete enum values (statuses, types, classifications)
   - Pagination behavior
   - Rate limit policies
   - Error response envelope format
4. **Test with sandbox credentials** before integrating into production.

---

## Contact

**IP Australia API Support:**
- **Email:** MDB-TDS@ipaustralia.gov.au
- **Phone:** 1300 65 10 10 (Australia) / +61 2 6283 2999 (International)
- **Website:** https://www.ipaustralia.gov.au/api-transaction-channel

