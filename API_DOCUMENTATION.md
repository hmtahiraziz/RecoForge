# AI Recommendations System API Documentation

## Overview

The AI Recommendations System provides intelligent product recommendations using OpenAI embeddings, FAISS vector search, and GPT-powered re-ranking. The system includes data ingestion, normalization, embedding generation, and user preference management.

## Table of Contents

1. [Authentication](#authentication)
2. [System Endpoints](#system-endpoints)
3. [Admin Endpoints](#admin-endpoints)
4. [Recommendation Endpoints](#recommendation-endpoints)
5. [Template Management](#template-management)
6. [Event Tracking](#event-tracking)
7. [Data Models](#data-models)
8. [Usage Examples](#usage-examples)
9. [Error Handling](#error-handling)

---

## Authentication

### JWT Token Authentication

Most endpoints require JWT authentication. Include the token in the Authorization header:

```http
Authorization: Bearer <your-jwt-token>
```

### Admin Authentication

Admin endpoints require SUPERADMIN role:

```http
Authorization: Bearer <admin-jwt-token>
```

---

## System Endpoints

### Health Check

Check if the recommendations service is healthy.

```http
GET /recs/health
```

**Response:**
```json
{
  "ok": true
}
```

**Usage Example:**
```bash
curl -X GET "http://localhost:8000/recs/health"
```

### Catalog Statistics

Get statistics about the catalog and index.

```http
GET /recs/catalog/stats
```

**Response:**
```json
{
  "catalog_items": 1000,
  "embeddings_count": 1000,
  "faiss_vectors": 1000,
  "faiss_dimension": 1536,
  "index_type": "IndexHNSWFlat",
  "last_updated": "2024-01-01T00:00:00Z"
}
```

**Usage Example:**
```bash
curl -X GET "http://localhost:8000/recs/catalog/stats"
```

---

## Admin Endpoints

### Rebuild Index

Rebuild the entire recommendation index (ingest + embeddings).

```http
POST /recs/admin/rebuild-index
Authorization: Bearer <admin-token>
```

**Response:**
```json
{
  "count": 1000,
  "dim": 1536,
  "index_type": "IndexHNSWFlat",
  "processing_time_ms": 45000
}
```

**Usage Example:**
```bash
curl -X POST "http://localhost:8000/recs/admin/rebuild-index" \
  -H "Authorization: Bearer <admin-token>"
```

### Reload Index

Reload the FAISS index in memory.

```http
POST /recs/admin/reload
Authorization: Bearer <admin-token>
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully reloaded index with 1000 vectors"
}
```

**Usage Example:**
```bash
curl -X POST "http://localhost:8000/recs/admin/reload" \
  -H "Authorization: Bearer <admin-token>"
```

---

## Recommendation Endpoints

### Get Recommendations

Get personalized product recommendations using the full AI pipeline.

```http
POST /recs/recommendations
```

**Request Body:**
```json
{
  "query": "I want a good beer for a BBQ",
  "answers": {
    "categories": ["Beer"],
    "style": "Stout",
    "abv_band": "mid",
    "pack_size": 24,
    "brand_pref": ["Sea Legs", "Coopers"],
    "dietary": [],
    "nice_to_have": ["citrus", "hoppy"],
    "ship_region": "AU-SA",
    "user_age": 28
  },
  "limit": 5
}
```

**Response:**
```json
{
  "query": "I want a good beer for a BBQ",
  "items": [
    {
      "sku": "SKU123",
      "title": "Coopers Original Pale Ale",
      "brand": "Coopers",
      "category": "Beer",
      "style": "Ale",
      "abv": 4.5,
      "price": 15.50,
      "score": 0.95,
      "reasons": [
        "Perfect for BBQ occasion",
        "Low ABV as preferred",
        "Coopers brand preference"
      ],
      "qty": 2
    }
  ],
  "confidence": 0.95,
  "subtotal": 31.00,
  "total_items": 1,
  "processing_time_ms": 150
}
```

**Usage Example:**
```bash
curl -X POST "http://localhost:8000/recs/recommendations" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "I want a good beer for a BBQ",
    "answers": {
      "categories": ["Beer"],
      "style": "Stout",
      "abv_band": "mid",
      "pack_size": 24,
      "brand_pref": ["Sea Legs", "Coopers"],
      "dietary": [],
      "nice_to_have": ["citrus", "hoppy"],
      "ship_region": "AU-SA",
      "user_age": 28
    },
    "limit": 5
  }'
```

---

## Template Management

### Save Template

Save user preference template for future use.

```http
POST /recs/templates
Authorization: Bearer <user-token>
```

**Request Body:**
```json
{
  "name": "BBQ Beer Preferences",
  "answers": {
    "categories": ["Beer"],
    "style": "Stout",
    "abv_band": "mid",
    "pack_size": 24,
    "brand_pref": ["Sea Legs", "Coopers"],
    "dietary": [],
    "nice_to_have": ["citrus", "hoppy"],
    "ship_region": "AU-SA",
    "user_age": 28
  }
}
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "message": "Template saved successfully"
}
```

**Usage Example:**
```bash
curl -X POST "http://localhost:8000/recs/templates" \
  -H "Authorization: Bearer <user-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "BBQ Beer Preferences",
    "answers": {
      "categories": ["Beer"],
      "style": "Stout",
      "abv_band": "mid",
      "pack_size": 24,
      "brand_pref": ["Sea Legs", "Coopers"],
      "dietary": [],
      "nice_to_have": ["citrus", "hoppy"],
      "ship_region": "AU-SA",
      "user_age": 28
    }
  }'
```

### Get Template

Retrieve a saved template by ID.

```http
GET /recs/templates/{template_id}
Authorization: Bearer <user-token>
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "template_name": "BBQ Beer Preferences",
  "items": {
    "categories": ["Beer"],
    "style": "Stout",
    "abv_band": "mid",
    "pack_size": 24,
    "brand_pref": ["Sea Legs", "Coopers"],
    "dietary": [],
    "nice_to_have": ["citrus", "hoppy"],
    "ship_region": "AU-SA",
    "user_age": 28
  },
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Usage Example:**
```bash
curl -X GET "http://localhost:8000/recs/templates/123e4567-e89b-12d3-a456-426614174000" \
  -H "Authorization: Bearer <user-token>"
```

---

## Event Tracking

### Log Event

Track user interactions with recommendations.

```http
POST /recs/events
Authorization: Bearer <user-token>
```

**Request Body:**
```json
{
  "sku": "SKU123",
  "action": "clicked",
  "meta": {
    "query": "I want a good beer for a BBQ",
    "position": 1,
    "score": 0.95,
    "template_id": "123e4567-e89b-12d3-a456-426614174000"
  },
  "template_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Response:**
```json
{
  "id": "456e7890-e89b-12d3-a456-426614174001",
  "message": "Event logged successfully"
}
```

**Usage Example:**
```bash
curl -X POST "http://localhost:8000/recs/events" \
  -H "Authorization: Bearer <user-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "SKU123",
    "action": "clicked",
    "meta": {
      "query": "I want a good beer for a BBQ",
      "position": 1,
      "score": 0.95
    }
  }'
```

**Available Actions:**
- `shown` - Recommendation was displayed to user
- `clicked` - User clicked on recommendation
- `added` - User added item to cart
- `purchased` - User purchased the item

---

## Data Models

### Answers Schema

User preference questionnaire answers:

```json
{
  "categories": ["Beer", "Wine"],           // Optional: Preferred categories
  "style": "Stout",                         // Optional: Product style
  "abv_band": "mid",                        // Optional: "low", "mid", "high"
  "pack_size": 24,                          // Optional: Preferred pack size
  "brand_pref": ["Sea Legs", "Coopers"],    // Optional: Preferred brands
  "dietary": ["gluten-free"],               // Optional: Dietary requirements
  "nice_to_have": ["citrus", "hoppy"],      // Optional: Nice-to-have features
  "ship_region": "AU-SA",                   // Optional: Shipping region
  "user_age": 28                            // Optional: User age (default: 21)
}
```

### RecommendationItem Schema

Individual recommendation item:

```json
{
  "sku": "SKU123",                          // Product SKU
  "title": "Coopers Original Pale Ale",     // Product title
  "brand": "Coopers",                       // Product brand
  "category": "Beer",                       // Product category
  "style": "Ale",                           // Product style
  "abv": 4.5,                              // Alcohol by volume %
  "price": 15.50,                          // Product price
  "score": 0.95,                           // Recommendation score (0.0-1.0)
  "reasons": [                              // Explanation reasons
    "Perfect for BBQ occasion",
    "Low ABV as preferred"
  ],
  "qty": 2                                 // Recommended quantity
}
```

---

## Usage Examples

### Complete Recommendation Journey

#### 1. Check System Health

```bash
curl -X GET "http://localhost:8000/recs/health"
```

#### 2. Get Catalog Statistics

```bash
curl -X GET "http://localhost:8000/recs/catalog/stats"
```

#### 3. Save User Preferences Template

```bash
curl -X POST "http://localhost:8000/recs/templates" \
  -H "Authorization: Bearer <user-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Beer Preferences",
    "answers": {
      "categories": ["Beer"],
      "abv_band": "low",
      "brand_pref": ["Coopers", "Corona"],
      "ship_region": "AU-NSW",
      "user_age": 25
    }
  }'
```

#### 4. Get Recommendations

```bash
curl -X POST "http://localhost:8000/recs/recommendations" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "I want a refreshing beer for summer",
    "answers": {
      "categories": ["Beer"],
      "abv_band": "low",
      "brand_pref": ["Coopers", "Corona"],
      "ship_region": "AU-NSW",
      "user_age": 25
    },
    "limit": 3
  }'
```

#### 5. Track User Interactions

```bash
# Log when recommendation is shown
curl -X POST "http://localhost:8000/recs/events" \
  -H "Authorization: Bearer <user-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "SKU123",
    "action": "shown",
    "meta": {
      "query": "I want a refreshing beer for summer",
      "position": 1
    }
  }'

# Log when user clicks on recommendation
curl -X POST "http://localhost:8000/recs/events" \
  -H "Authorization: Bearer <user-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "SKU123",
    "action": "clicked",
    "meta": {
      "query": "I want a refreshing beer for summer",
      "position": 1,
      "score": 0.95
    }
  }'
```

#### 6. Retrieve Saved Template

```bash
curl -X GET "http://localhost:8000/recs/templates/123e4567-e89b-12d3-a456-426614174000" \
  -H "Authorization: Bearer <user-token>"
```

### Admin Operations

#### 1. Rebuild Index (Admin Only)

```bash
curl -X POST "http://localhost:8000/recs/admin/rebuild-index" \
  -H "Authorization: Bearer <admin-token>"
```

#### 2. Reload Index (Admin Only)

```bash
curl -X POST "http://localhost:8000/recs/admin/reload" \
  -H "Authorization: Bearer <admin-token>"
```

---

## Error Handling

### Common Error Responses

#### 400 Bad Request
```json
{
  "detail": "Invalid action. Must be one of: ['shown', 'clicked', 'added', 'purchased']"
}
```

#### 401 Unauthorized
```json
{
  "detail": "Authorization header required"
}
```

#### 403 Forbidden
```json
{
  "detail": "SUPERADMIN role required"
}
```

#### 404 Not Found
```json
{
  "detail": "Template not found"
}
```

#### 500 Internal Server Error
```json
{
  "detail": "Error getting recommendations: OpenAI API rate limit exceeded"
}
```

### Error Handling Best Practices

1. **Always check HTTP status codes**
2. **Handle rate limiting with exponential backoff**
3. **Validate input data before sending requests**
4. **Implement retry logic for transient failures**
5. **Log errors for debugging and monitoring**

---

## Rate Limits and Performance

### OpenAI API Limits
- Embeddings: 3,000 requests per minute
- GPT-4.1-mini: 10,000 tokens per minute
- Batch processing is used to optimize API usage

### Performance Expectations
- Health check: < 10ms
- Catalog stats: < 100ms
- Recommendations: 1-3 seconds (depending on query complexity)
- Template operations: < 500ms
- Event logging: < 100ms

### Optimization Tips
1. **Use batch processing for multiple embeddings**
2. **Cache frequently accessed templates**
3. **Implement client-side rate limiting**
4. **Use appropriate limit values for recommendations**
5. **Monitor API usage and costs**

---

## Integration Examples

### JavaScript/Node.js

```javascript
const axios = require('axios');

class RecommendationsClient {
  constructor(baseURL, authToken) {
    this.client = axios.create({
      baseURL,
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json'
      }
    });
  }

  async getRecommendations(query, answers, limit = 5) {
    const response = await this.client.post('/recs/recommendations', {
      query,
      answers,
      limit
    });
    return response.data;
  }

  async saveTemplate(name, answers) {
    const response = await this.client.post('/recs/templates', {
      name,
      answers
    });
    return response.data;
  }

  async logEvent(sku, action, meta = {}) {
    const response = await this.client.post('/recs/events', {
      sku,
      action,
      meta
    });
    return response.data;
  }
}

// Usage
const client = new RecommendationsClient('http://localhost:8000', 'your-token');

const recommendations = await client.getRecommendations(
  'I want a good beer for a BBQ',
  {
    categories: ['Beer'],
    abv_band: 'mid',
    ship_region: 'AU-SA'
  }
);
```

### Python

```python
import requests
import json

class RecommendationsClient:
    def __init__(self, base_url, auth_token):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {auth_token}',
            'Content-Type': 'application/json'
        }

    def get_recommendations(self, query, answers, limit=5):
        response = requests.post(
            f'{self.base_url}/recs/recommendations',
            headers=self.headers,
            json={
                'query': query,
                'answers': answers,
                'limit': limit
            }
        )
        response.raise_for_status()
        return response.json()

    def save_template(self, name, answers):
        response = requests.post(
            f'{self.base_url}/recs/templates',
            headers=self.headers,
            json={
                'name': name,
                'answers': answers
            }
        )
        response.raise_for_status()
        return response.json()

    def log_event(self, sku, action, meta=None):
        response = requests.post(
            f'{self.base_url}/recs/events',
            headers=self.headers,
            json={
                'sku': sku,
                'action': action,
                'meta': meta or {}
            }
        )
        response.raise_for_status()
        return response.json()

# Usage
client = RecommendationsClient('http://localhost:8000', 'your-token')

recommendations = client.get_recommendations(
    'I want a good beer for a BBQ',
    {
        'categories': ['Beer'],
        'abv_band': 'mid',
        'ship_region': 'AU-SA'
    }
)
```

---

## Support and Troubleshooting

### Common Issues

1. **"Authorization header required"**
   - Ensure you're including the Authorization header with a valid JWT token

2. **"SUPERADMIN role required"**
   - Admin endpoints require a token with SUPERADMIN role

3. **"OpenAI API rate limit exceeded"**
   - Implement exponential backoff and retry logic
   - Consider reducing batch sizes

4. **"Template not found"**
   - Verify the template ID is correct
   - Ensure the user has access to the template

5. **"Invalid action"**
   - Use only the allowed action values: shown, clicked, added, purchased

### Getting Help

- Check the system health endpoint for service status
- Review catalog statistics for data availability
- Monitor API response times and error rates
- Check logs for detailed error information

---

## Changelog

### Version 1.0.0
- Initial release with full AI recommendations pipeline
- OpenAI embeddings and GPT re-ranking
- Template management and event tracking
- Secure admin endpoints
- Comprehensive API documentation
