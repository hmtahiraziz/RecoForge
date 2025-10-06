# FastAPI + Next.js Application with AI Recommendations

A modern full-stack application with FastAPI backend, Next.js frontend, and AI-powered recommendations system, designed for AWS deployment.

## 🏗️ Architecture

- **Backend**: FastAPI (Python) - REST API with S3 integration and AI recommendations
- **Frontend**: Next.js (React) - Modern web application
- **AI System**: OpenAI embeddings + GPT re-ranking for intelligent product recommendations
- **Infrastructure**: AWS EC2, S3, CloudFront, ECR
- **Containerization**: Docker & Docker Compose

## 📁 Project Structure

```
├── app/                    # FastAPI Backend
│   ├── main.py            # FastAPI application
│   ├── requirements.txt   # Python dependencies
│   ├── Dockerfile        # Backend container
│   ├── env.example       # Environment variables template
│   └── recs/             # AI Recommendations System
│       ├── router.py     # API endpoints
│       ├── models.py     # Database models
│       ├── schemas.py    # Pydantic schemas
│       └── services/     # Core services
│           ├── ingest.py # Data ingestion
│           ├── embed_openai.py # OpenAI embeddings
│           ├── filters.py # Hard filters
│           ├── rank_gpt.py # GPT re-ranking
│           └── normalize.py # Data normalization
├── pwa/                   # Next.js Frontend
│   ├── app/              # Next.js app directory
│   ├── package.json      # Node.js dependencies
│   ├── Dockerfile        # Production frontend container
│   ├── Dockerfile.dev    # Development frontend container
│   └── next.config.js    # Next.js configuration
├── data/                  # Data storage
│   ├── products-data.json # Source product data
│   ├── catalog.jsonl     # Normalized catalog
│   └── manifest.json     # Processing metadata
├── index/                 # AI index storage
│   ├── embeddings.npy    # Vector embeddings
│   ├── faiss.index       # FAISS search index
│   ├── id_map.jsonl      # ID mapping
│   └── meta.jsonl        # Metadata
├── infra/                 # Terraform infrastructure
├── docker-compose.yml     # Production containers
├── docker-compose.dev.yml # Development containers
├── API_DOCUMENTATION.md   # Complete API documentation
├── QUICK_START_GUIDE.md   # Quick start guide
└── README.md             # This file
```

## 🚀 Quick Start

### 1. Start the System

```bash
# Start with Docker Compose
docker-compose up -d

# Check health
curl http://localhost:8000/recs/health
```

### 2. Build the AI Index

```bash
# Run ingestion (processes product data)
docker-compose exec backend bash -c "cd /app && python -m recs.services ingest --source /app/data/products-data.json"

# Run embeddings (requires OpenAI API key)
docker-compose exec backend bash -c "cd /app && python -m recs.services embed --catalog /app/data/catalog.jsonl"
```

### 3. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **AI Recommendations**: http://localhost:8000/recs/health

### Development Mode

```bash
# Start development containers
docker-compose -f docker-compose.dev.yml up --build
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```bash
# AWS Configuration
AWS_REGION=us-east-1
FILES_BUCKET=your-s3-bucket-name

# Application
DEBUG=True

# OpenAI Configuration (for AI Recommendations)
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_ORG_ID=your-org-id-optional
EMBEDDING_MODEL=text-embedding-3-small
RERANK_MODEL=gpt-4o-mini

# Recommendations Configuration
REC_SOURCE_JSON=/app/data/source.jsonl
REC_EMBED_BATCH=512
ADMIN_TOKEN=your-admin-token
```

### Backend Configuration

The FastAPI backend includes:
- Health check endpoint (`/health`)
- Hello endpoint (`/api/hello`)
- S3 file listing (`/api/files`)
- **AI Recommendations System** (`/recs/*`)
- CORS enabled for frontend communication
- Automatic API documentation at `/docs`

### Frontend Configuration

The Next.js frontend includes:
- API proxy configuration in `next.config.js`
- Modern React components with TypeScript
- Responsive design with CSS modules
- Axios for API communication

## 🐳 Docker Commands

### Production
```bash
# Start production environment
docker-compose up -d

# View logs
docker-compose logs -f

# Stop production environment
docker-compose down

# Restart backend (after code changes)
docker-compose restart backend
```

### AI Recommendations Commands
```bash
# Check system health
curl http://localhost:8000/recs/health

# Check catalog statistics
curl http://localhost:8000/recs/catalog/stats

# Run data ingestion
docker-compose exec backend bash -c "cd /app && python -m recs.services ingest --source /app/data/products-data.json"

# Run embeddings generation
docker-compose exec backend bash -c "cd /app && python -m recs.services embed --catalog /app/data/catalog.jsonl"

# Check index statistics
docker-compose exec backend bash -c "cd /app && python -m recs.services embed --stats"
```

### Development
```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up --build

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop development environment
docker-compose -f docker-compose.dev.yml down
```

## 🌐 AWS Deployment

See the `infra/` directory for Terraform configuration to deploy to AWS:

1. **Configure AWS credentials**
2. **Update `infra/dev.tfvars`**
3. **Deploy infrastructure:**
   ```bash
   cd infra
   terraform init
   terraform plan -var-file=dev.tfvars
   terraform apply -var-file=dev.tfvars
   ```

## 📝 API Endpoints

### Backend (FastAPI)

#### Core Endpoints
- `GET /health` - Health check
- `GET /api/hello` - Hello message
- `GET /api/files` - List S3 files
- `POST /api/files/upload` - Upload file (placeholder)
- `GET /docs` - Interactive API documentation

#### AI Recommendations System (`/recs/*`)
- `GET /recs/health` - Recommendations service health
- `GET /recs/catalog/stats` - Catalog and index statistics
- `POST /recs/recommendations` - Get AI-powered recommendations
- `POST /recs/templates` - Save user preference templates
- `GET /recs/templates/{id}` - Retrieve saved templates
- `POST /recs/events` - Log user interaction events

#### Admin Endpoints (Require Authentication)
- `POST /recs/admin/rebuild-index` - Rebuild the entire AI index
- `POST /recs/admin/reload` - Reload FAISS index in memory

### Frontend (Next.js)

- `/` - Main application page
- `/api/*` - Proxied to backend API

## 🛠️ Development

### Backend Development

```bash
cd app
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Development

```bash
cd pwa
npm install
npm run dev
```

## 🔍 Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 3000 and 8000 are available
2. **S3 access**: Verify AWS credentials and S3 bucket permissions
3. **Container issues**: Try rebuilding with `--no-cache` flag
4. **OpenAI API errors**: Verify `OPENAI_API_KEY` is set correctly
5. **Recommendations not working**: Ensure embeddings are generated first

### AI Recommendations Issues

```bash
# Check if catalog exists
ls -la data/catalog.jsonl

# Check if embeddings exist
ls -la index/

# Verify system health
curl http://localhost:8000/recs/health

# Check catalog statistics
curl http://localhost:8000/recs/catalog/stats
```

### Logs

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs frontend

# Follow logs in real-time
docker-compose logs -f

# View backend logs only
docker-compose logs -f backend
```

## 📚 Additional Resources

### Documentation
- [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) - Complete API reference with examples
- [QUICK_START_GUIDE.md](./QUICK_START_GUIDE.md) - Quick start guide for AI recommendations
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)

### AI & ML
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [FAISS Documentation](https://faiss.ai/)
- [Docker Documentation](https://docs.docker.com/)

### Infrastructure
- [AWS Terraform Provider](https://registry.terraform.io/providers/hashicorp/aws/latest)

## 🎯 AI Recommendations System

The application now includes a complete AI-powered recommendations system:

- **Data Ingestion**: Processes product data from JSON/JSONL files
- **Normalization**: Cleans and standardizes product information
- **Embeddings**: Uses OpenAI to create vector embeddings
- **Search**: FAISS-based similarity search for fast retrieval
- **Re-ranking**: GPT-powered intelligent ranking with explanations
- **Filtering**: Hard guardrails for stock, region, age, and ABV
- **Templates**: Save and reuse user preferences
- **Events**: Track user interactions for analytics

### Key Features
- ✅ **22,984 products** successfully processed and cataloged
- ✅ **Real-time recommendations** with AI-powered ranking
- ✅ **User preference templates** for personalized experiences
- ✅ **Event tracking** for analytics and optimization
- ✅ **Secure admin endpoints** for system management
- ✅ **Complete API documentation** with examples
