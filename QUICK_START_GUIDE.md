# AI Recommendations System - Quick Start Guide

## 🚀 Quick Setup

### 1. Start the System

```bash
# Start with Docker Compose
docker-compose up -d

# Check health
curl http://localhost:8000/recs/health
```

### 2. Build the Index

```bash
# Run ingestion (Part 3)
docker-compose exec backend bash -c "cd /app && python3 -m recs.services ingest --source /app/data/products-data.json"

# Run embeddings (Part 4)
docker-compose exec backend bash -c "cd /app && python3 -m recs.services embed --catalog /app/data/catalog.jsonl"
```

**Note:** Make sure you have your OpenAI API key configured in your environment before running the embedding step.

---

## 📋 Common Use Cases

### Get Beer Recommendations

```bash
curl -X POST "http://localhost:8000/recs/recommendations" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "I want a good beer for a BBQ",
    "answers": {
      "categories": ["Beer"],
      "abv_band": "low",
      "ship_region": "AU-NSW",
      "user_age": 25
    },
    "limit": 5
  }'
```

### Save User Preferences

```bash
curl -X POST "http://localhost:8000/recs/templates" \
  -H "Authorization: Bearer <user-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Beer Preferences",
    "answers": {
      "categories": ["Beer"],
      "abv_band": "low",
      "brand_pref": ["Coopers", "Corona"]
    }
  }'
```

### Track User Interactions

```bash
curl -X POST "http://localhost:8000/recs/events" \
  -H "Authorization: Bearer <user-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "SKU123",
    "action": "clicked",
    "meta": {"position": 1, "score": 0.95}
  }'
```

---

## 🔧 Admin Operations

### Rebuild Index

```bash
curl -X POST "http://localhost:8000/recs/admin/rebuild-index" \
  -H "Authorization: Bearer <admin-token>"
```

### Check System Status

```bash
curl http://localhost:8000/recs/catalog/stats
```

---

## 📊 Data Pipeline

### 1. Data Ingestion
```bash
docker-compose exec backend bash -c "cd /app && python3 -m recs.services ingest --source /app/data/products-data.json"
```

### 2. Embedding Generation
```bash
docker-compose exec backend bash -c "cd /app && python3 -m recs.services embed --catalog /app/data/catalog.jsonl"
```

### 3. Index Statistics
```bash
docker-compose exec backend bash -c "cd /app && python3 -m recs.services embed --stats"
```

---

## 🎯 Key Features

- **AI-Powered**: OpenAI embeddings + GPT re-ranking
- **Smart Filtering**: Stock, region, age, ABV guardrails
- **User Templates**: Save and reuse preferences
- **Event Tracking**: Monitor user interactions
- **Secure Admin**: JWT-protected admin endpoints
- **Scalable**: FAISS indexing for fast search

---

## 📚 Full Documentation

See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for complete API reference and examples.
