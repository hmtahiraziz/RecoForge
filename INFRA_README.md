# AWS Single-App Host Deployment Scaffold

A cost-effective, production-ready deployment scaffold for hosting single applications on AWS using a single EC2 instance with Docker, Caddy reverse proxy, S3 file storage, optional CloudFront CDN, and optional ECR+CI/CD.

## Architecture Overview

```
Internet → CloudFront (optional) → EC2 (Caddy) → Docker Compose → App
                                    ↓
                                 S3 Bucket (files)
                                    ↓
                                 ECR (optional)
```

### Components

- **EC2 Instance**: Ubuntu 22.04 LTS (t2.micro) with Elastic IP
- **Security**: SSH restricted to your IP, HTTP/HTTPS open to world
- **Reverse Proxy**: Caddy with automatic HTTPS via Let's Encrypt
- **Container Runtime**: Docker CE + Docker Compose
- **File Storage**: S3 bucket (private, with optional CloudFront)
- **Container Registry**: ECR repository (optional)
- **CI/CD**: GitHub Actions workflow (optional)

### Cost Optimization

- Single t2.micro instance (~$8.50/month)
- No ALB, Route 53, or other expensive services
- Optional CloudFront for global CDN
- S3 storage costs only for actual usage
- ECR storage costs only when using CI/CD

## Quick Start

### Prerequisites

1. **Local Machine Setup**:
   ```bash
   # Install AWS CLI v2
   curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
   unzip awscliv2.zip
   sudo ./aws/install

   # Install other tools
   sudo apt-get update
   sudo apt-get install -y jq unzip git

   # Configure AWS credentials
   aws configure
   ```

2. **SSH Key Setup**:
   ```bash
   # Generate SSH key if you don't have one
   ssh-keygen -t ed25519 -C "your-email@example.com"

   # Get your public IP
   curl -s https://checkip.amazonaws.com
   ```

### Deployment Steps

1. **Clone and Configure**:
   ```bash
   git clone <this-repo>
   cd Setup-tr/infra

   # Copy and edit configuration
   cp .tfvars.example dev.tfvars
   nano dev.tfvars  # Edit with your values
   ```

2. **Deploy Infrastructure**:
   ```bash
   terraform init
   terraform plan -var-file=dev.tfvars
   terraform apply -auto-approve -var-file=dev.tfvars
   ```

3. **Connect and Verify**:
   ```bash
   # SSH to instance (use output from terraform)
   ssh -i ~/.ssh/id_ed25519 ubuntu@<instance_public_ip>

   # Verify services
   docker --version
   docker compose version
   caddy version
   ```

4. **Deploy Your App**:
   ```bash
   # On the EC2 instance
   cd /opt/app
   git clone <your-app-repo> app
   cd app

   # Copy appropriate docker-compose.yml (see templates below)
   # Edit environment variables
   docker compose up -d --build
   ```

## Configuration

### Terraform Variables

Edit `dev.tfvars` with your specific values:

```hcl
# Required
ssh_ingress_cidr = "203.0.113.1/32"  # Your public IP
public_key_path  = "~/.ssh/id_ed25519.pub"

# Optional toggles
create_s3         = true
create_cloudfront = false
create_ecr        = true
domain_name       = ""  # Set later for auto-TLS
```

### Caddy Configuration

**Initial Setup** (HTTP only):
```caddyfile
:80 {
    reverse_proxy localhost:3000
}
```

**With Domain** (auto-HTTPS):
```caddyfile
app.example.com {
    reverse_proxy localhost:3000
}
```

Reload Caddy after changes:
```bash
sudo systemctl reload caddy
```

## Docker Compose Templates

### FastAPI + React Stack

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.api
    ports:
      - "8000:8000"
    environment:
      - FILES_BUCKET=${FILES_BUCKET}
      - AWS_REGION=${AWS_REGION}
    volumes:
      - ./app:/app
    restart: unless-stopped

  web:
    build:
      context: .
      dockerfile: Dockerfile.web
    ports:
      - "3000:80"
    environment:
      - API_URL=http://localhost:8000
    depends_on:
      - api
    restart: unless-stopped
```

**Dockerfile.api**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .                             
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Dockerfile.web**:
```dockerfile
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Node + Express + React Stack

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.api
    ports:
      - "8000:8000"
    environment:
      - FILES_BUCKET=${FILES_BUCKET}
      - AWS_REGION=${AWS_REGION}
      - NODE_ENV=production
    volumes:
      - ./api:/app
    restart: unless-stopped

  web:
    build:
      context: .
      dockerfile: Dockerfile.web
    ports:
      - "3000:80"
    environment:
      - API_URL=http://localhost:8000
    depends_on:
      - api
    restart: unless-stopped
```

**Dockerfile.api**:
```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 8000

CMD ["npm", "start"]
```

**Dockerfile.web** (same as FastAPI version)

## S3 Integration

### Python (boto3)

```python
import boto3
import os

# Use default AWS provider chain (instance role)
s3_client = boto3.client('s3', region_name=os.environ['AWS_REGION'])
bucket_name = os.environ['FILES_BUCKET']

# Upload file
def upload_file(file_path, s3_key):
    s3_client.upload_file(file_path, bucket_name, s3_key)

# Download file
def download_file(s3_key, local_path):
    s3_client.download_file(bucket_name, s3_key, local_path)

# Generate presigned URL
def get_presigned_url(s3_key, expiration=3600):
    return s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket_name, 'Key': s3_key},
        ExpiresIn=expiration
    )
```

### Node.js (AWS SDK v3)

```javascript
import { S3Client, PutObjectCommand, GetObjectCommand } from '@aws-sdk/client-s3';
import { getSignedUrl } from '@aws-sdk/s3-request-presigner';

const s3Client = new S3Client({ region: process.env.AWS_REGION });
const bucketName = process.env.FILES_BUCKET;

// Upload file
async function uploadFile(fileBuffer, s3Key) {
    const command = new PutObjectCommand({
        Bucket: bucketName,
        Key: s3Key,
        Body: fileBuffer,
    });
    return await s3Client.send(command);
}

// Generate presigned URL
async function getPresignedUrl(s3Key, expiration = 3600) {
    const command = new GetObjectCommand({
        Bucket: bucketName,
        Key: s3Key,
    });
    return await getSignedUrl(s3Client, command, { expiresIn: expiration });
}
```

## CloudFront Setup

To enable CloudFront CDN:

1. **Update terraform variables**:
   ```hcl
   create_s3         = true
   create_cloudfront = true
   ```

2. **Redeploy**:
   ```bash
   terraform apply -var-file=dev.tfvars
   ```

3. **Use CloudFront domain**:
   ```bash
   # Get CloudFront domain from terraform output
   terraform output cloudfront_domain
   ```

4. **Update your app** to use CloudFront URLs for static assets.

## CI/CD with GitHub Actions

### GitHub Actions Workflow

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to AWS

on:
  push:
    branches: [main]

env:
  AWS_REGION: us-east-1
  ECR_REPOSITORY: single-app-host-api

jobs:
  deploy:
    runs-on: ubuntu-latest

    permissions:
      id-token: write
      contents: read

    steps:
    - name: Checkout
      uses: actions/checkout@v4

    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        role-to-assume: arn:aws:iam::<ACCOUNT_ID>:role/<GITHUB_OIDC_ROLE>
        aws-region: ${{ env.AWS_REGION }}

    - name: Login to Amazon ECR
      id: login-ecr
      uses: aws-actions/amazon-ecr-login@v2

    - name: Build and push image
      env:
        ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        IMAGE_TAG: ${{ github.sha }}
      run: |
        docker build -f Dockerfile.api -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
        docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
        docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:latest
        docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest

    - name: Deploy to EC2
      uses: appleboy/ssh-action@v1.0.0
      with:
        host: ${{ secrets.EC2_HOST }}
        username: ubuntu
        key: ${{ secrets.SSH_PRIVATE_KEY }}
        script: |
          cd /opt/app/app
          aws ecr get-login-password --region ${{ env.AWS_REGION }} | docker login --username AWS --password-stdin ${{ steps.login-ecr.outputs.registry }}
          docker compose pull
          docker compose up -d
```

### EC2 Deployment Script

Create `/opt/app/deploy.sh` on the EC2 instance:

```bash
#!/bin/bash
set -e

cd /opt/app/app

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com

# Pull latest images
docker compose pull

# Restart services
docker compose up -d

# Clean up old images
docker image prune -f

echo "Deployment completed at $(date)"
```

Make it executable:
```bash
chmod +x /opt/app/deploy.sh
```

## Manual Deployment

For manual deployments without CI/CD:

```bash
# SSH to instance
ssh -i ~/.ssh/id_ed25519 ubuntu@<instance_public_ip>

# Navigate to app directory
cd /opt/app/app

# Pull latest changes
git pull origin main

# Rebuild and restart
docker compose up -d --build

# Check logs
docker compose logs -f
```

## Domain Setup with Auto-TLS

1. **Point your domain** to the Elastic IP:
   ```
   A record: app.example.com → <elastic_ip>
   ```

2. **Update Caddyfile**:
   ```caddyfile
   app.example.com {
       reverse_proxy localhost:3000
   }
   ```

3. **Reload Caddy**:
   ```bash
   sudo systemctl reload caddy
   ```

4. **Verify HTTPS**:
   ```bash
   curl -I https://app.example.com
   ```

## Troubleshooting

### Common Issues

**CPU Credits Exhausted (t2.micro)**:
```bash
# Check CPU credits
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUCreditBalance \
  --dimensions Name=InstanceId,Value=<instance-id> \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average
```

**Add Swap File** (if not already present):
```bash
sudo fallocate -l 2G /swapfile2
sudo chmod 600 /swapfile2
sudo mkswap /swapfile2
sudo swapon /swapfile2
echo '/swapfile2 none swap sw 0 0' | sudo tee -a /etc/fstab
```

**Docker Issues**:
```bash
# Check Docker status
sudo systemctl status docker

# Restart Docker
sudo systemctl restart docker

# Check container logs
docker compose logs -f
```

**Caddy Issues**:
```bash
# Check Caddy status
sudo systemctl status caddy

# Test Caddyfile syntax
sudo caddy validate --config /etc/caddy/Caddyfile

# Reload Caddy
sudo systemctl reload caddy
```

**Memory Issues**:
```bash
# Check memory usage
free -h
docker stats

# Clean up Docker
docker system prune -f
docker volume prune -f
```

### Health Checks

**System Health Script**:
```bash
# Run the built-in health check
/opt/health-check.sh

# Check all services
sudo systemctl status docker caddy
docker compose ps
```

**Application Health**:
```bash
# Test API endpoint
curl http://localhost:8000/health

# Test web app
curl http://localhost:3000
```

## Security Considerations

- SSH access restricted to your IP only
- S3 bucket is private by default
- CloudFront uses Origin Access Control (OAC)
- All resources tagged for cost tracking
- IAM roles follow least-privilege principle
- Docker containers run as non-root users
- Caddy provides automatic HTTPS with Let's Encrypt

## Cost Monitoring

**Monthly Cost Estimate** (us-east-1):
- EC2 t2.micro: ~$8.50
- EBS storage (8GB): ~$0.80
- Elastic IP: ~$3.65 (if not attached to running instance)
- S3 storage: ~$0.023/GB/month
- CloudFront: ~$0.085/GB transfer
- ECR: ~$0.10/GB/month

**Total**: ~$13-15/month base cost

## Cleanup

To destroy all resources:
```bash
cd infra
terraform destroy -var-file=dev.tfvars
```

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Terraform and Docker logs
3. Verify AWS permissions and quotas
4. Check CloudWatch logs for detailed error information
