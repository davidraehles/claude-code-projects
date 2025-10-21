# API Contracts

**Feature**: Raedical.co Landing Page Redesign
**Date**: 2025-10-20

## Overview

This directory contains API contract specifications for the landing page's backend endpoints. The contracts are defined in OpenAPI 3.0.3 format and document the expected behavior of form submission and newsletter subscription APIs.

## Files

- **api-contract.yaml**: OpenAPI specification for all API endpoints

## Endpoints

### 1. Contact Form Submission

**Endpoint**: `POST /api/contact`

**Purpose**: Handles contact form submissions from visitors (FR-017, FR-018, FR-019)

**Request Body**:
```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "company": "Acme Corp",
  "phone": "+15551234567",  // Optional
  "message": "I'm interested in your services."
}
```

**Success Response** (200):
```json
{
  "success": true,
  "message": "Thank you for contacting us! We'll get back to you soon."
}
```

**Error Response** (400):
```json
{
  "success": false,
  "error": "Validation failed",
  "details": [
    {
      "field": "email",
      "message": "Please enter a valid email address"
    }
  ]
}
```

**Rate Limiting**: 5 requests per IP per hour

---

### 2. Newsletter Subscription

**Endpoint**: `POST /api/newsletter`

**Purpose**: Handles newsletter subscription requests (FR-021, FR-045)

**Request Body**:
```json
{
  "email": "subscriber@example.com",
  "consentGiven": true,
  "source": "footer"
}
```

**Success Response** (200):
```json
{
  "success": true,
  "message": "Successfully subscribed! Check your email to confirm."
}
```

**Already Subscribed** (409):
```json
{
  "success": false,
  "error": "This email is already subscribed to our newsletter."
}
```

**Rate Limiting**: 3 requests per IP per hour

---

### 3. Health Check

**Endpoint**: `GET /api/health`

**Purpose**: API health monitoring

**Response** (200):
```json
{
  "status": "ok",
  "timestamp": "2025-10-20T12:34:56Z"
}
```

---

## Implementation Notes

### Next.js API Routes

These contracts will be implemented as Next.js API routes:

```
app/api/
├── contact/
│   └── route.ts        # POST /api/contact
├── newsletter/
│   └── route.ts        # POST /api/newsletter
└── health/
    └── route.ts        # GET /api/health
```

### Example Implementation

```typescript
// app/api/contact/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { contactSubmissionSchema } from '@/lib/validation';
import { sendContactEmail } from '@/lib/email';
import { rateLimit } from '@/lib/rate-limit';

export async function POST(request: NextRequest) {
  // Rate limiting
  const rateLimitResult = await rateLimit(request, { max: 5, window: 3600 });
  if (!rateLimitResult.success) {
    return NextResponse.json(
      { success: false, error: 'Too many requests. Please try again later.' },
      { status: 429 }
    );
  }

  try {
    // Parse and validate request body
    const body = await request.json();
    const validatedData = contactSubmissionSchema.parse(body);

    // Send email via Resend/SendGrid
    await sendContactEmail(validatedData);

    return NextResponse.json({
      success: true,
      message: "Thank you for contacting us! We'll get back to you soon.",
    });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        {
          success: false,
          error: 'Validation failed',
          details: error.errors.map((e) => ({
            field: e.path.join('.'),
            message: e.message,
          })),
        },
        { status: 400 }
      );
    }

    return NextResponse.json(
      {
        success: false,
        error: 'Unable to send your message. Please try again or email us directly.',
      },
      { status: 500 }
    );
  }
}
```

---

## Validation Rules

All validation rules are defined in the data model and enforced both client-side (React Hook Form + Zod) and server-side (API routes).

### Contact Form Validation

| Field | Rules |
|-------|-------|
| name | Required, 1-100 chars, trimmed |
| email | Required, valid email format, lowercase, trimmed |
| company | Required, 1-200 chars, trimmed |
| phone | Optional, E.164 format |
| message | Required, 10-5000 chars, trimmed |

### Newsletter Validation

| Field | Rules |
|-------|-------|
| email | Required, valid email format, lowercase, trimmed |
| consentGiven | Required, must be `true` |
| source | Required, enum: 'hero' \| 'footer' \| 'contact-form' |

---

## Security Considerations

1. **Rate Limiting**: Prevents spam and abuse
2. **Input Validation**: Server-side validation prevents malicious input
3. **HTTPS**: All API calls must be over HTTPS in production
4. **CORS**: Configure appropriate CORS headers for API routes
5. **Privacy**: Email service handles PII storage and compliance

---

## Testing

### Contract Testing

Use the OpenAPI spec for automated contract testing:

```bash
# Validate API responses against contract
npm run test:contract
```

### Example Test

```typescript
import { describe, it, expect } from 'vitest';
import { POST } from '@/app/api/contact/route';

describe('POST /api/contact', () => {
  it('returns 400 for invalid email', async () => {
    const request = new Request('http://localhost/api/contact', {
      method: 'POST',
      body: JSON.stringify({
        name: 'Test',
        email: 'invalid-email',
        company: 'Test Co',
        message: 'Test message here',
      }),
    });

    const response = await POST(request as any);
    const data = await response.json();

    expect(response.status).toBe(400);
    expect(data.success).toBe(false);
    expect(data.error).toBe('Validation failed');
  });
});
```

---

## Viewing the API Specification

You can view the OpenAPI spec using:

1. **Swagger Editor**: https://editor.swagger.io/ (paste the YAML content)
2. **Redoc**: Generate documentation with `npx @redocly/cli preview-docs api-contract.yaml`
3. **VS Code**: Install "OpenAPI (Swagger) Editor" extension

---

## Email Service Integration

The API routes will integrate with an email service (Resend or SendGrid) to deliver contact form submissions and newsletter subscriptions.

### Resend Example

```typescript
import { Resend } from 'resend';

const resend = new Resend(process.env.RESEND_API_KEY);

export async function sendContactEmail(data: ContactSubmissionInput) {
  await resend.emails.send({
    from: 'contact@raedical.co',
    to: 'team@raedical.co',
    subject: `New contact form submission from ${data.company}`,
    html: `
      <h2>New Contact Form Submission</h2>
      <p><strong>Name:</strong> ${data.name}</p>
      <p><strong>Email:</strong> ${data.email}</p>
      <p><strong>Company:</strong> ${data.company}</p>
      ${data.phone ? `<p><strong>Phone:</strong> ${data.phone}</p>` : ''}
      <p><strong>Message:</strong></p>
      <p>${data.message}</p>
    `,
  });
}
```

---

## Next Steps

1. Implement API routes in Next.js (`/app/api/`)
2. Set up email service (Resend/SendGrid)
3. Configure rate limiting middleware
4. Write integration tests for each endpoint
5. Set up monitoring and error tracking

---

**References**:
- [Data Model](../data-model.md)
- [Research](../research.md)
- [Specification](../spec.md)
