# Bulk Import API Contracts

**Feature**: Bulk Recipe Import from Parent Websites  
**Version**: 1.0  
**Base Path**: `/api/v1/bulk-import`

## Overview

This document defines the API contracts for the bulk recipe import feature. All endpoints require authentication via JWT token in the Authorization header.

---

## Endpoints

### 1. Start Bulk Import

Initiates a new bulk import job from a parent URL.

**Endpoint**: `POST /api/v1/bulk-import/start`

**Authentication**: Required

**Request Body**:
```json
{
  "parent_url": "https://www.ottolenghi.co.uk/recipes",
  "options": {
    "max_recipes": 100,
    "overwrite_duplicates": false,
    "rate_limit_per_second": 1.0
  }
}
```

**Request Schema**:
- `parent_url` (string, required): The URL of the parent page containing recipe links
- `options` (object, optional):
  - `max_recipes` (integer, optional, default: 100): Maximum number of recipes to import
  - `overwrite_duplicates` (boolean, optional, default: false): Whether to overwrite existing recipes
  - `rate_limit_per_second` (float, optional, default: 1.0): Rate limit for requests to target site

**Response**: `201 Created`
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "discovering",
  "parent_url": "https://www.ottolenghi.co.uk/recipes",
  "started_at": "2025-12-15T20:00:00Z"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid URL or options
- `401 Unauthorized`: Missing or invalid authentication token
- `429 Too Many Requests`: User has too many active import jobs

---

### 2. Get Job Status

Retrieves the current status of a bulk import job.

**Endpoint**: `GET /api/v1/bulk-import/{job_id}`

**Authentication**: Required

**Path Parameters**:
- `job_id` (UUID, required): The unique identifier of the import job

**Response**: `200 OK`
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "in_progress",
  "parent_url": "https://www.ottolenghi.co.uk/recipes",
  "progress": {
    "total_discovered": 50,
    "total_processed": 25,
    "total_success": 22,
    "total_failed": 2,
    "total_duplicates": 1,
    "percentage": 50,
    "estimated_time_remaining_seconds": 150
  },
  "started_at": "2025-12-15T20:00:00Z",
  "completed_at": null
}
```

**Response Schema**:
- `job_id` (UUID): Job identifier
- `status` (enum): One of: `discovering`, `in_progress`, `completed`, `cancelled`, `failed`
- `parent_url` (string): The parent URL being processed
- `progress` (object):
  - `total_discovered` (integer): Number of recipe URLs discovered
  - `total_processed` (integer): Number of recipes processed
  - `total_success` (integer): Number of successfully imported recipes
  - `total_failed` (integer): Number of failed imports
  - `total_duplicates` (integer): Number of duplicates skipped
  - `percentage` (integer): Progress percentage (0-100)
  - `estimated_time_remaining_seconds` (integer, nullable): Estimated seconds until completion
- `started_at` (datetime): When the job started
- `completed_at` (datetime, nullable): When the job completed

**Error Responses**:
- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: User doesn't own this job
- `404 Not Found`: Job not found

---

### 3. Stream Progress Updates (SSE)

Streams real-time progress updates for a bulk import job using Server-Sent Events.

**Endpoint**: `GET /api/v1/bulk-import/{job_id}/progress`

**Authentication**: Required

**Path Parameters**:
- `job_id` (UUID, required): The unique identifier of the import job

**Response**: `200 OK` (text/event-stream)

**Event Stream Format**:
```
data: {"status": "discovering", "discovered": 10}

data: {"status": "in_progress", "processed": 1, "success": 1, "current_recipe": "Pasta with Tomatoes"}

data: {"status": "in_progress", "processed": 2, "success": 2, "current_recipe": "Roasted Vegetables"}

data: {"status": "in_progress", "processed": 3, "success": 2, "failed": 1, "error": "No recipe found"}

data: {"status": "completed", "processed": 50, "success": 47, "failed": 2, "duplicates": 1}
```

**Event Data Schema**:
- `status` (enum): Current job status
- `discovered` (integer, optional): Number of URLs discovered (during discovery phase)
- `processed` (integer, optional): Number of recipes processed so far
- `success` (integer, optional): Number of successful imports
- `failed` (integer, optional): Number of failed imports
- `duplicates` (integer, optional): Number of duplicates skipped
- `current_recipe` (string, optional): Title of currently processing recipe
- `error` (string, optional): Error message for last failed recipe

**Connection**:
- Client should maintain connection until status is `completed`, `cancelled`, or `failed`
- Auto-reconnect on disconnect with exponential backoff
- Send `Connection: keep-alive` header

**Error Responses**:
- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: User doesn't own this job
- `404 Not Found`: Job not found

---

### 4. Cancel Import Job

Cancels a running bulk import job.

**Endpoint**: `POST /api/v1/bulk-import/{job_id}/cancel`

**Authentication**: Required

**Path Parameters**:
- `job_id` (UUID, required): The unique identifier of the import job

**Response**: `200 OK`
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "cancelled",
  "recipes_imported": 25,
  "cancelled_at": "2025-12-15T20:05:00Z"
}
```

**Response Schema**:
- `job_id` (UUID): Job identifier
- `status` (string): Will be "cancelled"
- `recipes_imported` (integer): Number of recipes successfully imported before cancellation
- `cancelled_at` (datetime): When the job was cancelled

**Error Responses**:
- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: User doesn't own this job
- `404 Not Found`: Job not found
- `409 Conflict`: Job is not in a cancellable state (already completed or cancelled)

---

### 5. Retry Failed Imports

Re-attempts to import recipes that failed in a previous bulk import job.

**Endpoint**: `POST /api/v1/bulk-import/{job_id}/retry`

**Authentication**: Required

**Path Parameters**:
- `job_id` (UUID, required): The unique identifier of the original import job

**Response**: `201 Created`
```json
{
  "job_id": "650e8400-e29b-41d4-a716-446655440111",
  "original_job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "in_progress",
  "retry_count": 3,
  "started_at": "2025-12-15T20:10:00Z"
}
```

**Response Schema**:
- `job_id` (UUID): New job identifier for the retry
- `original_job_id` (UUID): The original job being retried
- `status` (string): Status of the retry job
- `retry_count` (integer): Number of failed URLs being retried
- `started_at` (datetime): When the retry started

**Error Responses**:
- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: User doesn't own this job
- `404 Not Found`: Job not found
- `400 Bad Request`: Job has no failed imports to retry

---

### 6. Get Import Results

Retrieves detailed results of a completed bulk import job.

**Endpoint**: `GET /api/v1/bulk-import/{job_id}/results`

**Authentication**: Required

**Path Parameters**:
- `job_id` (UUID, required): The unique identifier of the import job

**Query Parameters**:
- `page` (integer, optional, default: 1): Page number for pagination
- `per_page` (integer, optional, default: 20, max: 100): Results per page
- `status` (enum, optional): Filter by import status (`success`, `failed`, `duplicate`)

**Response**: `200 OK`
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "summary": {
    "total_discovered": 50,
    "total_success": 47,
    "total_failed": 2,
    "total_duplicates": 1
  },
  "successful_recipes": [
    {
      "recipe_id": 123,
      "title": "Pasta with Tomatoes",
      "url": "https://www.ottolenghi.co.uk/recipes/pasta-tomatoes",
      "imported_at": "2025-12-15T20:02:30Z"
    }
  ],
  "failed_imports": [
    {
      "url": "https://www.ottolenghi.co.uk/recipes/invalid-page",
      "error": "No recipe found on page"
    },
    {
      "url": "https://www.ottolenghi.co.uk/recipes/blocked",
      "error": "Scraping blocked (403)"
    }
  ],
  "duplicate_recipes": [
    {
      "url": "https://www.ottolenghi.co.uk/recipes/existing-recipe",
      "existing_recipe_id": 101,
      "reason": "URL match"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_pages": 3,
    "total_items": 50
  }
}
```

**Response Schema**:
- `job_id` (UUID): Job identifier
- `summary` (object): Overall statistics
  - `total_discovered` (integer): Total recipes discovered
  - `total_success` (integer): Successful imports
  - `total_failed` (integer): Failed imports
  - `total_duplicates` (integer): Duplicates skipped
- `successful_recipes` (array): List of successfully imported recipes
  - `recipe_id` (integer): ID of the imported recipe
  - `title` (string): Recipe title
  - `url` (string): Source URL
  - `imported_at` (datetime): Import timestamp
- `failed_imports` (array): List of failed imports
  - `url` (string): URL that failed
  - `error` (string): Error message
- `duplicate_recipes` (array): List of duplicates skipped
  - `url` (string): URL of duplicate
  - `existing_recipe_id` (integer): ID of existing recipe
  - `reason` (string): Why it was marked as duplicate
- `pagination` (object): Pagination metadata

**Error Responses**:
- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: User doesn't own this job
- `404 Not Found`: Job not found

---

## Common Response Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters or body
- `401 Unauthorized`: Authentication required or token invalid
- `403 Forbidden`: Authenticated but not authorized to access resource
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource state conflict
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

---

## Authentication

All endpoints require a valid JWT token in the Authorization header:

```
Authorization: Bearer <jwt_token>
```

The token must contain:
- `user_id`: The authenticated user's ID
- `exp`: Token expiration timestamp

---

## Rate Limiting

API requests are subject to rate limiting:
- **Per user**: 10 active bulk import jobs maximum
- **Per endpoint**: 100 requests per minute
- **SSE connections**: 5 concurrent connections per user

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
```

---

## Error Response Format

All error responses follow this format:

```json
{
  "error": {
    "code": "INVALID_URL",
    "message": "The provided URL is not accessible or invalid",
    "details": {
      "url": "https://invalid-site.com",
      "reason": "DNS resolution failed"
    }
  }
}
```

**Error Codes**:
- `INVALID_URL`: URL is malformed or inaccessible
- `MAX_JOBS_EXCEEDED`: User has too many active jobs
- `JOB_NOT_FOUND`: Job ID doesn't exist
- `UNAUTHORIZED`: Authentication failed
- `FORBIDDEN`: User doesn't own the resource
- `INVALID_STATE`: Operation not allowed in current job state
- `RATE_LIMIT_EXCEEDED`: Too many requests

---

## WebSocket Alternative (Future)

For clients that cannot use SSE, a WebSocket endpoint may be provided in the future:

```
ws://api.example.com/v1/bulk-import/{job_id}/ws
```

The WebSocket would send the same JSON messages as SSE data payloads.
