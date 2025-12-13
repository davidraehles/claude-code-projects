# Security Middleware Quick Reference

## Rate Limiting

### Current Limits (requests per minute per user)
- **Cart Creation** (`POST /api/v1/grocery-carts/*`): 10 req/min
- **Cart Updates** (`PUT/PATCH /api/v1/grocery-carts/*`): 20 req/min
- **Product Searches** (`*/knuspr/*/search*`): 30 req/min
- **Default** (other endpoints): 60 req/min

### Response Headers
```http
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1702345678
```

### 429 Response
```json
{
  "error": "rate_limit_exceeded",
  "message": "Rate limit exceeded for cart_creation. Please try again later.",
  "limit": 10,
  "window_seconds": 60,
  "retry_after_seconds": 45
}
```

Headers:
```http
Retry-After: 45
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1702345678
```

### Exempted Endpoints
- `/health`
- `/metrics`
- `/`
- `/api/docs`
- `/api/redoc`
- `/openapi.json`

## Security Headers

### Always Added
```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
X-Download-Options: noopen
X-Permitted-Cross-Domain-Policies: none
```

### Production Only (HTTPS)
```http
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

## Configuration

### Rate Limiting
```env
RATE_LIMIT_CART_CREATION=10      # req/min
RATE_LIMIT_CART_UPDATES=20        # req/min
RATE_LIMIT_PRODUCT_SEARCHES=30    # req/min
RATE_LIMIT_DEFAULT=60             # req/min
```

### Security
```env
ENFORCE_HTTPS=false               # Enable HTTPS redirect
HSTS_MAX_AGE=31536000            # HSTS max age (seconds)
HSTS_INCLUDE_SUBDOMAINS=true     # Apply to subdomains
HSTS_PRELOAD=false               # HSTS preload list
CSP_ENABLED=false                # Enable CSP
```

### Redis (Rate Limiting)
```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

## Testing

### Test Security Headers
```bash
curl -v http://localhost:8000/health 2>&1 | grep -E "X-|Referrer"
```

### Test Rate Limit Headers
```bash
curl -v http://localhost:8000/api/v1/grocery-carts \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test Rate Limiting
```bash
# Make 15 requests (limit is 10/min for cart creation)
for i in {1..15}; do
  curl -X POST http://localhost:8000/api/v1/grocery-carts \
    -H "Authorization: Bearer YOUR_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"name":"test"}' \
    -w "\nStatus: %{http_code}\n"
  sleep 0.5
done
```

### Run Test Script
```bash
cd /home/darae/meal-planner/backend
./test_security_middleware.sh
```

## Monitoring

### Check Rate Limit Violations
```bash
docker logs recipe-api | grep "Rate limit exceeded"
```

### Check Redis Connection
```bash
docker logs recipe-api | grep "rate limit middleware"
```

### View Metrics
```bash
curl http://localhost:8000/metrics | grep -E "rate_limit|http_request"
```

## Troubleshooting

### Rate Limiting Not Working
1. Check Redis connection: `docker logs recipe-api | grep Redis`
2. Verify environment variables are set
3. Check user authentication (JWT token)
4. Verify endpoint matches rate limit patterns

### Security Headers Missing
1. Check middleware is registered in main.py
2. Verify no errors in app logs
3. Test with curl -v to see all headers

### HTTPS Redirect Not Working
1. Ensure `ENFORCE_HTTPS=true` in production
2. Check `APP_ENV=production`
3. Verify not using SecurityHeadersMiddleware (use SecurityMiddleware instead)

### Redis Connection Failed
- Rate limiting falls back to in-memory storage
- Check Redis is running: `docker ps | grep redis`
- Verify REDIS_HOST and REDIS_PORT

## Architecture

### Middleware Order (LIFO execution)
1. CORSMiddleware (outermost)
2. SecurityHeadersMiddleware
3. RateLimitMiddleware
4. PrometheusMiddleware (innermost)

### Rate Limit Storage
- **Primary:** Redis (distributed, persistent)
- **Fallback:** In-memory (single instance only)

### User Identification
1. JWT token → user_id (primary)
2. IP address (fallback for anonymous)

## Best Practices

1. **Adjust limits** based on usage patterns
2. **Monitor logs** for rate limit violations
3. **Use SecurityHeadersMiddleware** in development
4. **Enable ENFORCE_HTTPS** in production (if handling HTTPS at app level)
5. **Set up alerts** for excessive rate limiting
6. **Keep HSTS_PRELOAD=false** unless you understand the implications

## Production Checklist

- [ ] Redis connection configured
- [ ] Environment variables set
- [ ] Rate limits adjusted for production traffic
- [ ] HTTPS properly configured
- [ ] ENFORCE_HTTPS set appropriately
- [ ] Monitoring set up for rate limit violations
- [ ] Health checks exempted from rate limiting
- [ ] Test rate limiting with real traffic patterns

## Support

For detailed documentation, see:
- [SECURITY_MIDDLEWARE_IMPLEMENTATION_REPORT.md](SECURITY_MIDDLEWARE_IMPLEMENTATION_REPORT.md)
- [.env.example](../../.env.example)

For issues, check:
- Application logs: `docker logs recipe-api`
- Redis logs: `docker logs recipe-redis`
- Prometheus metrics: `http://localhost:8000/metrics`
