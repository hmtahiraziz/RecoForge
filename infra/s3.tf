# S3 Bucket (only created if create_s3=true)
resource "random_id" "bucket_suffix" {
  count       = var.create_s3 ? 1 : 0
  byte_length = 4
}

resource "aws_s3_bucket" "main" {
  count  = var.create_s3 ? 1 : 0
  bucket = var.s3_bucket_name != "" ? var.s3_bucket_name : "${var.project_name}-files-${random_id.bucket_suffix[0].hex}"

  tags = merge(var.tags, {
    Name = "${var.project_name}-s3-bucket"
  })
}

# S3 Bucket versioning
resource "aws_s3_bucket_versioning" "main" {
  count  = var.create_s3 ? 1 : 0
  bucket = aws_s3_bucket.main[0].id
  versioning_configuration {
    status = "Enabled"
  }
}

# S3 Bucket server-side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "main" {
  count  = var.create_s3 ? 1 : 0
  bucket = aws_s3_bucket.main[0].id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
    bucket_key_enabled = true
  }
}

# S3 Bucket public access block
resource "aws_s3_bucket_public_access_block" "main" {
  count  = var.create_s3 ? 1 : 0
  bucket = aws_s3_bucket.main[0].id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# S3 Bucket CORS configuration (for web app access)
resource "aws_s3_bucket_cors_configuration" "main" {
  count  = var.create_s3 ? 1 : 0
  bucket = aws_s3_bucket.main[0].id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "PUT", "POST", "DELETE", "HEAD"]
    allowed_origins = ["*"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}
