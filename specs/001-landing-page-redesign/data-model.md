# Data Model: Raedical.co Landing Page Redesign

**Date**: 2025-10-20
**Feature**: Landing Page Redesign
**Source**: Extracted from [spec.md](spec.md) Key Entities and Functional Requirements

## Overview

This document defines the data structures and validation rules for the landing page. Since this is primarily a static site, most "entities" are TypeScript interfaces for type safety and validation schemas for form handling.

---

## Entity 1: Contact Submission

**Description**: Represents an inquiry or contact request from a visitor.

**Source Requirements**: FR-017, FR-018, FR-019, FR-022

### Fields

| Field | Type | Required | Validation Rules | Notes |
|-------|------|----------|------------------|-------|
| `name` | string | Yes | Min 1 char, Max 100 chars | Full name of the person submitting |
| `email` | string | Yes | Valid email format (RFC 5322) | Primary contact method |
| `company` | string | Yes | Min 1 char, Max 200 chars | Company/organization name |
| `phone` | string | No | Optional, E.164 format if provided | Secondary contact method |
| `message` | string | Yes | Min 10 chars, Max 5000 chars | The inquiry or message content |
| `submittedAt` | timestamp | Auto | ISO 8601 datetime | When form was submitted |
| `userAgent` | string | Auto | Max 500 chars | Browser info for debugging |
| `ipAddress` | string | Auto | IPv4 or IPv6 format | For spam prevention (privacy compliant) |

### TypeScript Interface

```typescript
export interface ContactSubmission {
  name: string;
  email: string;
  company: string;
  phone?: string;
  message: string;
  submittedAt: string; // ISO 8601
  userAgent: string;
  ipAddress: string;
}
```

### Validation Schema (Zod)

```typescript
import { z } from 'zod';

export const contactSubmissionSchema = z.object({
  name: z
    .string()
    .min(1, 'Name is required')
    .max(100, 'Name must be less than 100 characters')
    .trim(),

  email: z
    .string()
    .email('Please enter a valid email address')
    .toLowerCase()
    .trim(),

  company: z
    .string()
    .min(1, 'Company is required')
    .max(200, 'Company name must be less than 200 characters')
    .trim(),

  phone: z
    .string()
    .regex(/^\+?[1-9]\d{1,14}$/, 'Please enter a valid phone number')
    .optional()
    .or(z.literal('')), // Allow empty string

  message: z
    .string()
    .min(10, 'Message must be at least 10 characters')
    .max(5000, 'Message must be less than 5000 characters')
    .trim(),
});

export type ContactSubmissionInput = z.infer<typeof contactSubmissionSchema>;
```

### State Transitions

```
[User fills form] → VALIDATING
    ↓ (validation passes)
SUBMITTING → [API call to email service]
    ↓ (success)
SUBMITTED → [Show success message]
    ↓ (error)
FAILED → [Show error message, allow retry]
```

### Error Handling

| Error Scenario | User Message | Action |
|----------------|--------------|--------|
| Validation failure | Field-specific error below input | Highlight field, prevent submit |
| Network error | "Unable to send message. Please try again." | Allow retry |
| Email service error | "Something went wrong. Please email us directly at [email]" | Provide fallback contact method |
| Rate limit exceeded | "Too many requests. Please wait a moment." | Implement client-side rate limiting |
| Duplicate submission | Silently accept (show success) | Prevent accidental duplicates with timestamp check |

---

## Entity 2: Newsletter Subscription

**Description**: Represents a visitor's opt-in to receive updates via email.

**Source Requirements**: FR-021, FR-045

### Fields

| Field | Type | Required | Validation Rules | Notes |
|-------|------|----------|------------------|-------|
| `email` | string | Yes | Valid email format (RFC 5322) | Subscriber email address |
| `subscribedAt` | timestamp | Auto | ISO 8601 datetime | When subscription occurred |
| `source` | string | Auto | Max 50 chars | Where subscription came from (e.g., "footer", "contact-form") |
| `consentGiven` | boolean | Yes | Must be true | GDPR/CCPA compliance |
| `ipAddress` | string | Auto | IPv4 or IPv6 format | For compliance audit trail |

### TypeScript Interface

```typescript
export interface NewsletterSubscription {
  email: string;
  subscribedAt: string; // ISO 8601
  source: 'hero' | 'footer' | 'contact-form';
  consentGiven: boolean;
  ipAddress: string;
}
```

### Validation Schema (Zod)

```typescript
export const newsletterSubscriptionSchema = z.object({
  email: z
    .string()
    .email('Please enter a valid email address')
    .toLowerCase()
    .trim(),

  consentGiven: z
    .boolean()
    .refine((val) => val === true, {
      message: 'You must agree to receive emails',
    }),

  source: z.enum(['hero', 'footer', 'contact-form']),
});

export type NewsletterSubscriptionInput = z.infer<typeof newsletterSubscriptionSchema>;
```

### State Transitions

```
[User enters email + checks consent] → VALIDATING
    ↓ (validation passes)
SUBSCRIBING → [API call to email service]
    ↓ (success)
SUBSCRIBED → [Show success message]
    ↓ (error - email exists)
ALREADY_SUBSCRIBED → [Show "already subscribed" message]
    ↓ (error - service down)
FAILED → [Show error, allow retry]
```

### Double Opt-In Flow (Recommended)

```
1. User submits email
2. API sends confirmation email with unique token
3. User clicks link in email
4. API confirms subscription
5. User is added to mailing list
```

---

## Entity 3: Page Content

**Description**: Represents the various content blocks that make up the landing page. This is primarily for content management and is likely stored as static data or in a CMS.

**Source Requirements**: FR-001 through FR-016

### Content Structure

```typescript
export interface PageContent {
  hero: HeroContent;
  about: AboutContent;
  features: FeatureContent[];
  socialProof: SocialProofContent;
  seo: SEOContent;
}

export interface HeroContent {
  headline: string;          // FR-001: Main value proposition
  subheadline: string;       // FR-002: Supporting context
  ctaText: string;           // FR-003: Button text
  ctaLink: string;           // FR-003: Button destination (e.g., "#contact")
  backgroundImage?: {
    src: string;
    alt: string;
    width: number;
    height: number;
  };                         // FR-004: Hero visual
}

export interface AboutContent {
  heading: string;
  body: string[];            // Array of paragraphs
  keyPoints?: string[];      // FR-007: Unique selling points
}

export interface FeatureContent {
  id: string;
  icon: string;              // Path to icon or icon name
  title: string;
  description: string;
  order: number;             // Display order
}

export interface SocialProofContent {
  testimonials: Testimonial[];
  clientLogos?: ClientLogo[];
  stats?: Statistic[];
}

export interface Testimonial {
  id: string;
  quote: string;
  author: {
    name: string;
    title?: string;          // FR-014: Attribution
    company?: string;        // FR-014: Attribution
    avatar?: string;
  };
}

export interface ClientLogo {
  id: string;
  name: string;              // For alt text
  logoUrl: string;
  websiteUrl?: string;
}

export interface Statistic {
  id: string;
  value: string;             // e.g., "10,000+"
  label: string;             // e.g., "Happy Customers"
  source?: string;           // FR-016: Context and sourcing
}

export interface SEOContent {
  title: string;             // FR-032: Page title
  description: string;       // FR-032: Meta description
  ogImage: string;           // FR-032: Open Graph image
  keywords?: string[];       // Optional: meta keywords
  canonicalUrl: string;
}
```

### Content Validation

```typescript
export const heroContentSchema = z.object({
  headline: z.string().min(10).max(100),
  subheadline: z.string().min(20).max(200),
  ctaText: z.string().min(3).max(30),
  ctaLink: z.string().url().or(z.string().regex(/^#/)), // URL or anchor
  backgroundImage: z.object({
    src: z.string(),
    alt: z.string().min(10),
    width: z.number().positive(),
    height: z.number().positive(),
  }).optional(),
});
```

---

## Entity 4: Analytics Event

**Description**: Represents user interactions tracked for measuring page effectiveness.

**Source Requirements**: FR-043, FR-044, SC-008

### Event Types

```typescript
export type AnalyticsEventType =
  | 'page_view'
  | 'cta_click'
  | 'form_start'
  | 'form_submit'
  | 'form_error'
  | 'newsletter_subscribe'
  | 'external_link_click'
  | 'scroll_depth';

export interface AnalyticsEvent {
  eventType: AnalyticsEventType;
  eventData?: Record<string, any>;
  timestamp: string; // ISO 8601
  userId?: string; // Anonymous identifier
  sessionId?: string;
}
```

### Event Definitions

| Event Type | When Triggered | Event Data |
|------------|----------------|------------|
| `page_view` | Page loads | `{ referrer: string, page_title: string }` |
| `cta_click` | User clicks CTA button | `{ cta_location: string, cta_text: string }` |
| `form_start` | User focuses first form field | `{ form_type: 'contact' \| 'newsletter' }` |
| `form_submit` | Form successfully submitted | `{ form_type: 'contact' \| 'newsletter', success: boolean }` |
| `form_error` | Validation error occurs | `{ form_type: string, error_field: string, error_type: string }` |
| `newsletter_subscribe` | Newsletter signup completes | `{ source: string }` |
| `external_link_click` | User clicks external link | `{ url: string, text: string }` |
| `scroll_depth` | User scrolls to milestone | `{ depth: 25 \| 50 \| 75 \| 100 }` |

### TypeScript Interface

```typescript
export interface PageViewEvent {
  eventType: 'page_view';
  eventData: {
    referrer: string;
    pageTitle: string;
    userAgent: string;
  };
}

export interface CTAClickEvent {
  eventType: 'cta_click';
  eventData: {
    ctaLocation: 'hero' | 'footer' | 'sticky';
    ctaText: string;
    destination: string;
  };
}

export interface FormSubmitEvent {
  eventType: 'form_submit';
  eventData: {
    formType: 'contact' | 'newsletter';
    success: boolean;
    errorMessage?: string;
  };
}
```

---

## Validation Summary

### Form Validation Rules Matrix

| Field | Min Length | Max Length | Format | Required | Special Rules |
|-------|-----------|-----------|--------|----------|---------------|
| Name | 1 | 100 | Text | Yes | Trim whitespace |
| Email | - | - | RFC 5322 | Yes | Lowercase, trim |
| Company | 1 | 200 | Text | Yes | Trim whitespace |
| Phone | - | - | E.164 | No | Optional field |
| Message | 10 | 5000 | Text | Yes | Trim whitespace |

### Error Message Standards

- **Field-level errors**: Display immediately below input field
- **Form-level errors**: Display at top of form
- **Success messages**: Display in place of form with clear next steps
- **ARIA announcements**: All errors announced to screen readers

---

## Data Privacy & Security

### GDPR/CCPA Compliance (FR-045)

1. **Consent**: Newsletter requires explicit checkbox (consentGiven field)
2. **Data Minimization**: Only collect necessary fields
3. **Right to Access**: Provide mechanism to request data
4. **Right to Deletion**: Provide mechanism to delete data
5. **Data Storage**: Clarify where data is stored (email service provider)

### Security Measures

1. **Input Sanitization**: All text inputs sanitized before sending to API
2. **XSS Prevention**: React automatically escapes rendered content
3. **CSRF Protection**: Not applicable for stateless API calls
4. **Rate Limiting**: Prevent form spam (max 5 submissions per IP per hour)
5. **Email Validation**: Server-side validation in addition to client-side

### PII (Personally Identifiable Information)

Fields containing PII:
- Name
- Email
- Phone
- IP Address

**Handling**: All PII transmitted over HTTPS, stored by email service provider (Resend/SendGrid) with their security guarantees.

---

## Relationships

```
PageContent (1)
├── Hero (1)
├── About (1)
├── Features (1..6)
└── SocialProof (1)
    ├── Testimonials (0..*)
    ├── ClientLogos (0..*)
    └── Statistics (0..*)

User Interaction (1)
├── ContactSubmission (0..*)
├── NewsletterSubscription (0..1)
└── AnalyticsEvents (0..*)
```

---

## Next Steps

With data model complete, proceed to:
1. Generate API contracts (`contracts/` directory)
2. Generate quickstart guide
3. Update agent context with data models

All entities from spec.md are now defined with validation rules and TypeScript interfaces.
