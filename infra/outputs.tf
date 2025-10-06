output "instance_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_eip.main.public_ip
}

output "ssh_example" {
  description = "SSH command example to connect to the instance"
  value       = "ssh -i ~/.ssh/id_ed25519 ubuntu@${aws_eip.main.public_ip}"
}

output "s3_bucket_name" {
  description = "Name of the S3 bucket (if created)"
  value       = var.create_s3 ? aws_s3_bucket.main[0].bucket : null
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket (if created)"
  value       = var.create_s3 ? aws_s3_bucket.main[0].arn : null
}

output "cloudfront_domain" {
  description = "CloudFront distribution domain name (if created)"
  value       = var.create_cloudfront ? aws_cloudfront_distribution.main[0].domain_name : null
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID (if created)"
  value       = var.create_cloudfront ? aws_cloudfront_distribution.main[0].id : null
}

output "ecr_repository_url" {
  description = "ECR repository URL (if created)"
  value       = var.create_ecr ? aws_ecr_repository.main[0].repository_url : null
}

output "ecr_repository_arn" {
  description = "ECR repository ARN (if created)"
  value       = var.create_ecr ? aws_ecr_repository.main[0].arn : null
}

output "instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.main.id
}

output "security_group_id" {
  description = "Security group ID"
  value       = aws_security_group.main.id
}
