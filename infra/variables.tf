variable "project_name" {
  description = "Name of the project used for resource naming"
  type        = string
  default     = "single-app-host"
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t2.micro"
}

variable "ssh_ingress_cidr" {
  description = "CIDR block for SSH access (e.g., x.x.x.x/32)"
  type        = string
}

variable "public_key_path" {
  description = "Path to the public key file for SSH access"
  type        = string
}

variable "create_s3" {
  description = "Whether to create S3 bucket for file storage"
  type        = bool
  default     = true
}

variable "s3_bucket_name" {
  description = "Name of the S3 bucket (leave empty for auto-generated name)"
  type        = string
  default     = ""
}

variable "create_cloudfront" {
  description = "Whether to create CloudFront distribution (requires create_s3=true)"
  type        = bool
  default     = false
}

variable "create_ecr" {
  description = "Whether to create ECR repository for container images"
  type        = bool
  default     = true
}

variable "domain_name" {
  description = "Domain name for the application (used later with Caddy for auto-TLS)"
  type        = string
  default     = ""
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default = {
    Project     = "single-app-host"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}
