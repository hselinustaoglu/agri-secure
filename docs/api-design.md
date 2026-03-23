# AgriSecure — API Design Guidelines

> **Status:** Placeholder — this document will be expanded as individual services are built.

---

## 1. RESTful Conventions

All AgriSecure backend services expose RESTful HTTP APIs following these conventions:

### Resource naming

- Use **plural nouns** for resource collections: `/farmers`, `/prices`, `/alerts`.
- Use **kebab-case** for multi-word resource names: `/market-prices`, `/early-warnings`.
- Nest resources only one level deep where a clear ownership relationship exists:
  ```
  GET /farmers/{farmer_id}/advisories
  GET /markets/{market_id}/prices
  ```

### HTTP methods

| Method | Use |
|--------|-----|
| `GET` | Retrieve a resource or collection (read-only, idempotent) |
| `POST` | Create a new resource |
| `PUT` | Replace a resource entirely |
| `PATCH` | Partially update a resource |
| `DELETE` | Remove a resource |

### Status codes

| Code | Meaning |
|------|---------|
| `200 OK` | Successful read / update |
| `201 Created` | Successful resource creation (include `Location` header) |
| `204 No Content` | Successful deletion |
| `400 Bad Request` | Invalid request payload or parameters |
| `401 Unauthorized` | Missing or invalid authentication token |
| `403 Forbidden` | Authenticated but not authorised for this action |
| `404 Not Found` | Resource does not exist |
| `422 Unprocessable Entity` | Validation error (FastAPI default) |
| `500 Internal Server Error` | Unexpected server-side error |

---

## 2. Authentication

> **Placeholder** — the authentication strategy will be finalised during implementation.

Planned approach:
- **JWT (JSON Web Tokens)** for API authentication.
- Tokens issued by a central identity service (or Keycloak/Auth0 integration).
- Short-lived access tokens (15 minutes) + refresh token rotation.
- Service-to-service calls authenticated via shared secrets or mTLS in production.

All protected endpoints require an `Authorization: Bearer <token>` header.

---

## 3. Versioning Strategy

APIs are versioned via a **URL path prefix**:

```
/api/v1/farmers
/api/v2/farmers   ← when breaking changes are needed
```

- Version `v1` is the initial production version.
- Deprecated versions are supported for a minimum of **6 months** after a new version ships.
- Breaking changes always require a new major version.
- Non-breaking additions (new optional fields, new endpoints) are made in-place without bumping the version.

---

## 4. Request & Response Format

- All request and response bodies use **JSON** (`Content-Type: application/json`).
- Timestamps use **ISO 8601** format in UTC: `"2026-03-23T09:00:00Z"`.
- Pagination uses **cursor-based** or **offset/limit** pagination depending on the endpoint:
  ```json
  {
    "data": [...],
    "meta": {
      "total": 150,
      "limit": 20,
      "offset": 0
    }
  }
  ```
- Empty collections return `[]`, not `null`.

---

## 5. Error Handling

All errors return a consistent JSON envelope:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable description of the error",
    "details": [
      {
        "field": "phone_number",
        "issue": "Must be a valid E.164 format phone number"
      }
    ]
  }
}
```

| Field | Description |
|-------|-------------|
| `code` | Machine-readable error code (SCREAMING_SNAKE_CASE) |
| `message` | Human-readable summary |
| `details` | Optional array of per-field validation issues |

---

## 6. Filtering, Sorting, and Search

- **Filtering**: Use query parameters matching field names: `GET /prices?crop=maize&region=nairobi`
- **Sorting**: `?sort=price&order=desc` (default: ascending)
- **Full-text search**: `?q=<search-term>` where supported
- **Date ranges**: `?from=2026-01-01&to=2026-03-31`

---

## 7. Documentation

Each service will expose auto-generated interactive API docs at:

- **Swagger UI**: `GET /docs`
- **ReDoc**: `GET /redoc`
- **OpenAPI JSON**: `GET /openapi.json`

Powered by FastAPI's built-in OpenAPI support.
