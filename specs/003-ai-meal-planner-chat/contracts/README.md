# API Contracts - AI Meal Planner Chat

**Purpose**: OpenAPI 3.1 specifications for all REST APIs and WebSocket endpoints

**Status**: Phase 1 Design Complete (Ready for Implementation)

---

## API Overview

### 4 Primary APIs

1. **Chat API** (`chat-api.openapi.yaml`)
   - Create and manage chat sessions
   - Send/receive messages
   - WebSocket real-time communication
   - Session history and context management

2. **Preferences API** (`preferences-api.openapi.yaml`)
   - Save dietary and ethnological preferences
   - Retrieve and update user profile
   - Validate preference combinations
   - Allergen and dietary restriction definitions

3. **Voice API** (`voice-api.openapi.yaml`)
   - Speech-to-text (Deepgram integration)
   - Text-to-speech (Azure Neural TTS)
   - Voice recording management
   - Audio caching and cost optimization

4. **Meal Plan API** (`meal-plan-api.openapi.yaml`)
   - Generate personalized meal plans
   - Save and manage plans
   - Request alternative meals
   - Generate shopping lists

---

## File Structure

```
contracts/
├── README.md                           # This file
├── chat-api.openapi.yaml              # 500+ lines
├── preferences-api.openapi.yaml       # 400+ lines
├── voice-api.openapi.yaml             # 450+ lines
└── meal-plan-api.openapi.yaml         # 550+ lines
```

**Total Contract Lines**: 1,900+ lines of specification

---

## Using These Contracts

### 1. Code Generation

Generate server stubs and client SDKs:

```bash
# Generate Python server (FastAPI)
openapi-generator generate \
  -i chat-api.openapi.yaml \
  -g python-fastapi \
  -o backend/generated

# Generate TypeScript client (Next.js)
openapi-generator generate \
  -i chat-api.openapi.yaml \
  -g typescript-fetch \
  -o frontend/src/api/generated
```

### 2. Documentation

Serve interactive API documentation:

```bash
# Using Swagger UI
docker run -p 8080:8080 \
  -v $(pwd):/swagger \
  swaggerapi/swagger-ui \
  -u file:///swagger/chat-api.openapi.yaml

# Using ReDoc
docker run -p 8080:8080 \
  -e SPEC_URL=/swagger/chat-api.openapi.yaml \
  -v $(pwd):/swagger \
  redocly/redoc
```

Visit: http://localhost:8080

### 3. Contract Testing

Validate API implementation against contract:

```python
# pytest with openapi-spec-validator
import pytest
from openapi_spec_validator import validate_spec

def test_chat_api_contract():
    with open('chat-api.openapi.yaml') as f:
        spec = yaml.safe_load(f)
    validate_spec(spec)  # Raises exception if invalid

# Test actual API against contract
from schemathesis import from_file

schema = from_file("chat-api.openapi.yaml")

@schema.parametrize()
def test_api(case):
    response = requests.request(*case.as_requests_kwargs())
    assert case.is_response_valid(response)
```

### 4. Mock Server

Generate mock API server for frontend development:

```bash
# Using Prism
npm install -g @stoplight/prism-cli

prism mock chat-api.openapi.yaml --host 0.0.0.0 --port 8000
```

Frontend can now develop against mock server without backend.

---

## API Endpoints Summary

### Chat API

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/chat/sessions` | Create chat session |
| GET | `/chat/sessions` | List user's sessions |
| GET | `/chat/sessions/{id}` | Get session details |
| PATCH | `/chat/sessions/{id}` | Update session status |
| POST | `/chat/sessions/{id}/messages` | Send message |
| GET | `/chat/sessions/{id}/messages` | Get message history |
| GET | `/chat/sessions/{id}/messages/{msg_id}` | Get single message |
| POST | `/chat/sessions/{id}/summarize` | Force summarization |
| **WebSocket** | `/ws/chat/sessions/{id}` | Real-time messages |

### Preferences API

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/preferences` | Get user preferences |
| POST | `/preferences` | Save preferences (new) |
| PATCH | `/preferences` | Update specific fields |
| DELETE | `/preferences` | Delete all preferences |
| POST | `/preferences/validate` | Validate without saving |
| GET | `/preferences/allergen-list` | Get allergen definitions |
| GET | `/preferences/dietary-restrictions-list` | Get restriction definitions |
| GET | `/preferences/cuisine-list` | Get cuisine definitions |

### Voice API

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/voice/transcribe` | Convert audio to text |
| POST | `/voice/synthesize` | Convert text to audio |
| GET | `/voice/recordings/{id}` | Get recording details |
| DELETE | `/voice/recordings/{id}` | Delete recording (GDPR) |
| GET | `/voice/health` | Check service status |

### Meal Plan API

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/meal-plans` | Generate meal plan |
| GET | `/meal-plans` | List saved plans |
| GET | `/meal-plans/{id}` | Get plan details |
| PATCH | `/meal-plans/{id}` | Update plan |
| DELETE | `/meal-plans/{id}` | Delete plan |
| POST | `/meal-plans/{id}/save` | Save/approve plan |
| POST | `/meal-plans/{id}/alternative-meal` | Get alternative |
| GET | `/meal-plans/{id}/shopping-list` | Generate shopping list |

---

## Schema Definitions

### Core Objects

**ChatSession**
- Represents a conversation thread
- Links to user and contains message history
- Tracks tokens used and generation costs

**ChatMessage**
- Individual message in a session
- Stores sender, content, intent, timestamp
- Tracks tokens for cost monitoring

**UserPreferences**
- Dietary restrictions (vegan, keto, etc)
- Allergies with severity levels
- Cuisine preferences
- Cooking skill, time constraints, equipment
- Household composition

**MealPlan**
- Collection of meals for N days
- Tracks compliance with allergies
- Stores user satisfaction feedback
- Versioning (parent_plan_id for modifications)

**VoiceRecording**
- Transcribed audio with confidence score
- Auto-expires after 24 hours (GDPR)
- Tracks provider (Deepgram, Web Speech, etc)

**AudioCache**
- TTS output cached for 30 days
- Keyed by SHA256 hash of input
- Tracks hit count for optimization

---

## Authentication

All endpoints use **Bearer Token (JWT)**:

```bash
curl -X GET http://localhost:8000/v1/chat/sessions \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Exceptions** (no auth required):
- GET `/preferences/allergen-list`
- GET `/preferences/dietary-restrictions-list`
- GET `/preferences/cuisine-list`
- GET `/voice/health`

---

## Error Handling

All APIs use consistent error format:

```json
{
  "code": "ERROR_CODE_HERE",
  "message": "Human-readable error message",
  "details": {
    "field": "Additional context"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Meaning |
|------|-------------|---------|
| UNAUTHORIZED | 401 | Missing/invalid authentication |
| NOT_FOUND | 404 | Resource not found |
| VALIDATION_ERROR | 400 | Invalid input |
| CONFLICTING_PREFERENCES | 409 | Preferences contradict each other |
| FAILED_ALLERGEN_CHECK | 400 | Meal contains user's allergen |
| RATE_LIMIT_EXCEEDED | 429 | Too many requests |
| INTERNAL_ERROR | 500 | Server error |

---

## Rate Limiting

**Default Limits**:

| Endpoint Category | Requests/Minute | Notes |
|------------------|-----------------|-------|
| Chat (messages) | 60 | Per session |
| Chat (sessions) | 10 | Create/delete limited |
| Preferences | 30 | CRUD operations |
| Voice (STT) | 120 | Speech-to-text calls |
| Voice (TTS) | 120 | Text-to-speech calls |
| Meal Plans | 20 | Generation requests |

**Headers in Response**:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1700000000
```

---

## WebSocket Protocol (Chat API)

### Connection

```
wss://api.claude-code-projects.com/ws/chat/sessions/{session_id}?token=JWT_TOKEN
```

### Message Format

**Client → Server** (send message):
```json
{
  "type": "message",
  "content": "I'm vegetarian and allergic to peanuts"
}
```

**Server → Client** (new message):
```json
{
  "type": "message:new",
  "message": {
    "id": "msg-uuid",
    "sender": "user",
    "content": "...",
    "tokens_used": 150,
    "timestamp": "2025-11-18T10:30:00Z"
  }
}
```

**Server → Client** (AI response):
```json
{
  "type": "message:new",
  "message": {
    "id": "msg-uuid",
    "sender": "assistant",
    "content": "Great! A vegetarian diet means... [long response]",
    "tokens_used": 250,
    "timestamp": "2025-11-18T10:30:05Z"
  }
}
```

**Server → Client** (meal plan ready):
```json
{
  "type": "meal_plan:generated",
  "meal_plan": {
    "id": "plan-uuid",
    "meals": [...],
    "status": "review"
  }
}
```

### Events

| Event | Sender | Meaning |
|-------|--------|---------|
| `message:new` | Server | New message in conversation |
| `message:processing` | Server | AI is generating response |
| `meal_plan:generated` | Server | Meal plan ready for review |
| `meal_plan:allergen_violation` | Server | Meal contains allergen |
| `connection:closed` | Server | Session ending |
| `error` | Server | Error occurred |

---

## Cost Tracking

All endpoints return cost information:

```json
{
  "cost": {
    "amount_cents": 15,
    "currency": "USD"
  },
  "tokens_used": 250
}
```

**Monthly Budget Estimation**:
- Claude API: ~$0.026 per plan
- Speech-to-Text: ~$0.0023 per minute
- Text-to-Speech: ~$0.00016 per 100 chars

---

## Pagination

List endpoints support pagination:

```bash
curl -X GET 'http://localhost:8000/v1/chat/sessions?limit=20&offset=0'
```

**Response**:
```json
{
  "sessions": [...],
  "pagination": {
    "total": 150,
    "limit": 20,
    "offset": 0
  }
}
```

---

## Validation Rules

### Preferences Validation

```yaml
dietary_restrictions:
  - enum: [vegan, vegetarian, keto, low_carb, gluten_free, kosher, halal, paleo, whole30, low_fat]

allergies:
  - required: ['allergen', 'severity']
  - severity: [mild, moderate, severe]

cooking_skill:
  - enum: [beginner, intermediate, advanced]

household_size:
  - min: 1
  - max: 20
```

### Message Validation

```yaml
content:
  - minLength: 1
  - maxLength: 5000

intent_detected:
  - enum: [request_meal_plan, modify_preference, ask_clarification, approve_plan, ...]
```

### Meal Plan Validation

```yaml
plan_start_date:
  - cannot be in the past

passed_allergen_check:
  - MUST be true before saving

duration_days:
  - min: 1
  - max: 365
```

---

## Implementation Notes

### Database Integration

Each API endpoint maps to database models:

| API | Model | Table |
|-----|-------|-------|
| Chat POST | ChatSession | chat_sessions |
| Chat Message POST | ChatMessage | chat_messages |
| Preferences POST | UserPreference | user_preferences |
| Meal Plan POST | MealPlan | meal_plans |
| Voice Transcribe | VoiceRecording | voice_recordings |

### Cache Integration

Responses are cached strategically:

| Endpoint | Cache Duration | Key |
|----------|-----------------|-----|
| GET preferences | 24 hours | `user:{user_id}:preferences` |
| GET chat session | 5 minutes | `session:{session_id}` |
| GET allergen list | Indefinite | `static:allergen_list` |
| Voice synthesize | 30 days | `tts:hash:{text_hash}` |

### Async Processing

These operations are async (return immediately, process in background):

- Meal plan generation (returns job_id)
- Message processing (via WebSocket)
- Audio transcription (return recording_id)

---

## Compliance & Security

### GDPR

- ✅ Voice recordings auto-delete after 24 hours
- ✅ User can request preference deletion
- ✅ User deletion cascade (chat, plans, preferences)
- ✅ Audit trail retained (separate deletion for analytics)

### Data Privacy

- ✅ All endpoints require authentication
- ✅ HTTPS enforced (TLS 1.3+)
- ✅ Passwords hashed (bcrypt)
- ✅ API keys never logged
- ✅ Voice audio not stored permanently

### Accessibility

- ✅ All text endpoints support voice (WebSocket)
- ✅ All meal plans can be generated as audio
- ✅ API responses include ARIA labels
- ✅ Error messages are descriptive

---

## Testing

### Unit Tests
Test individual endpoint behavior:

```python
def test_create_chat_session():
    response = client.post("/chat/sessions", ...)
    assert response.status_code == 201
    assert "session_id" in response.json()
```

### Integration Tests
Test end-to-end flows:

```python
def test_chat_to_meal_plan_flow():
    # 1. Create session
    # 2. Send preferences
    # 3. Generate meal plan
    # 4. Verify compliance
```

### Contract Tests
Validate against OpenAPI spec:

```python
def test_api_matches_openapi():
    spec = load_openapi("chat-api.openapi.yaml")
    response = client.post("/chat/sessions", ...)
    assert validate_response(response, spec)
```

### E2E Tests (Playwright)
Test from user's perspective:

```typescript
test('user can create meal plan', async ({ page }) => {
  await page.goto('http://localhost:3000/chat');
  await page.fill('textarea', 'I am vegetarian');
  await page.click('button:has-text("Generate Plan")');
  await expect(page).toContainText('Your Meal Plan');
});
```

---

## Future Enhancements

### v1.1 (Post-MVP)
- [ ] Bulk meal plan generation
- [ ] Meal plan sharing and collaboration
- [ ] Advanced filtering (price range, prep time)
- [ ] Recipe ratings and reviews

### v2.0 (Future)
- [ ] Integration with grocery delivery APIs
- [ ] Calendar synchronization
- [ ] Nutritional tracking
- [ ] Multi-language support

---

## References

- **OpenAPI Specification**: https://spec.openapis.org/oas/v3.1.0
- **JSON Schema**: https://json-schema.org/
- **Data Model**: [data-model.md](../data-model.md)
- **Implementation Plan**: [plan.md](../plan.md)
- **Feature Specification**: [spec.md](../spec.md)

---

## Support

For API contract questions:

1. Check OpenAPI specification (YAML files)
2. Review Swagger UI: http://localhost:8000/docs
3. Read implementation notes above
4. Check integration tests for examples

---

**Status**: ✅ Phase 1 Complete - Ready for Implementation (Phase 2)
